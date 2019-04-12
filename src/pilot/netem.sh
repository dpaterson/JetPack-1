#!/bin/bash

TC=tc
if [ -a $DEV0 ]
then
    DEV0=eth0
fi

if [ -a $DEV1 ]
then
    DEV1=eth1
fi

if [ $DEV1 == "null" ]
then
    DUAL=0
fi

if [ -z $1 ]
then
    cat <<EOF
$0 delay [ceiling] [additional_delay]

Where:
        delay is a plain number representing the ms of delay
        ceiling is a rate with unit, or 0 for no rate limit
        additional_delay is any additional parameters to pass to netem

Examples:

     o  To clear all rate limits:
        $0 0

     o  To set a basic round trip time of 8ms, with 4ms of variability
        (ie: 4-12ms variable latency):
        $0 8 0 2ms

     o  To set a maximum line rate of 10 0mbit/s with no latency:
        $0 0 100mbit

     o  To set a maximum line rate of 1.54 mbit/s with 65-85ms of
        variable latency:
        $0 75 1540kbit 5ms


     o  To set a maximum line rate of 10 mbit/s with 480-520ms of
        variable latency, with 2% packet loss:
        $0 500 10mbit 10ms loss 1.5%

Note:   The additional_delay and packet loss is added to both interfaces,
        doubling the amount of variability.

EOF
        exit
fi
DEL=$1
RATE=$2

# Flush any existing rate limits:
$TC qdisc del dev $DEV0 root 2> /dev/null
if [ -z $DUAL ] ; then
$TC qdisc del dev $DEV1 root 2> /dev/null
fi

shift
shift

if [ -z $DUAL ] ; then
    DELAY=`expr $DEL / 2 2> /dev/null`
    if [ -z $DELAY ]
    then
        echo "Bad delay number: $DEL"
        exit
    fi
else
    DELAY=$DEL
fi

MTU=1520

if [ -z $RATE ]
then
    RATE=0
fi

if [ ! $RATE = 0 ]
then
    LEN=`echo $RATE | wc -c`
    LAST=`expr $LEN - 4`
    UNIT=`echo $RATE | cut -c $LAST-`
    LAST=`expr $LAST - 1`
    BITS_PER_SECOND=`echo $RATE | cut -c 1-$LAST`

    if [ "$UNIT" = "" ]
    then
        echo "Did not specify a unit for the rate limit"
        exit
    fi

    if [ "$UNIT" = "gbit" ]
    then
        BITS_PER_SECOND=`expr $BITS_PER_SECOND \* 1000000000`
    fi
    if [ "$UNIT" = "mbit" ]
    then
        BITS_PER_SECOND=`expr $BITS_PER_SECOND \* 1000000`
    fi
    if [ "$UNIT" = "kbit" ]
    then
        BITS_PER_SECOND=`expr $BITS_PER_SECOND \* 1000`
    fi

    BUFFERS_PER_SECOND=`expr $BITS_PER_SECOND / $MTU`

    if [ $BITS_PER_SECOND -lt 1000000 ]
    then
        # Rate is less than 1mbit/s, we need to throttle the burst
        PEAK=`expr $BITS_PER_SECOND + 8`

        PEAKRATE="burst $MTU mtu $MTU limit $MTU peakrate 1mbit"
        PEAKRATE="burst $MTU latency 1ms peakrate $PEAK minburst $MTU"
    else
        # Convert the bits to bytes to packets...
        BURST=`expr $BITS_PER_SECOND / $MTU / 8`
        if [ $BURST -lt $MTU ]
        then
            BURST=$MTU
        fi

        PEAKRATE="burst $BURST mtu $MTU limit $BURST"
    fi

    if [ -z $DEL ] ; then DEL=0 ; fi
    LIMIT=1000;

    if [ $DEL -gt 0 ]
    then
        LIMIT=`expr $DELAY \* $BUFFERS_PER_SECOND / 1000`
    if [ $LIMIT -lt 1 ] ; then LIMIT=1 ; fi
    else
        LIMIT=`expr $BUFFERS_PER_SECOND / 1000`
    if [ $LIMIT -lt 1 ] ; then LIMIT=1 ; fi
    fi

    TBF="root handle 1: tbf rate $RATE $PEAKRATE"
    echo $TC qdisc add dev $DEV0 $TBF
    $TC qdisc add dev $DEV0 $TBF
if [ -z $DUAL ] ; then
    $TC qdisc add dev $DEV1 $TBF
fi

    NETEM="parent 1: handle 10: netem delay ${DELAY}ms $* limit $LIMIT"
    echo $TC qdisc add dev $DEV0 $NETEM
    $TC qdisc add dev $DEV0 $NETEM
if [ -z $DUAL ] ; then
    $TC qdisc add dev $DEV1 $NETEM
fi

    PFIFO="parent 10:1 pfifo limit $LIMIT";
    echo $TC qdisc add dev $DEV0 $PFIFO
    $TC qdisc add dev $DEV0 $PFIFO
if [ -z $DUAL ] ; then
    $TC qdisc add dev $DEV1 $PFIFO
fi

else
    if [ ! -z $DEL -a $DEL -gt 0 ]
    then
        LIMIT=`expr $DELAY \* 1000000`
        if [ $LIMIT -lt 3200 ] ; then LIMIT=3200 ; fi
        DELAY="delay ${DELAY}ms $* limit $LIMIT"

        echo $TC qdisc add dev $DEV0 root handle 1: netem $DELAY
        $TC qdisc add dev $DEV0 root handle 1: netem $DELAY

if [ -z $DUAL ] ; then
        $TC qdisc add dev $DEV1 root handle 1: netem $DELAY
fi

        PFIFO="parent 1:1 pfifo limit $LIMIT";
        echo $TC qdisc add dev $DEV0 $PFIFO
        $TC qdisc add dev $DEV0 $PFIFO
if [ -z $DUAL ] ; then
        $TC qdisc add dev $DEV1 $PFIFO
fi
    fi
fi

