#!/bin/bash
#set -x

JVM_OPTIONS="-Djava.class.path="
JVM_OPTIONS+="../../gears_runtime/bin/:"
JVM_OPTIONS+="../../gears_runtime/lib/jackson-annotations-2.11.0.jar:"
JVM_OPTIONS+="../../gears_runtime/lib/jackson-core-2.11.0.jar:"
JVM_OPTIONS+="../../gears_runtime/lib/jackson-databind-2.11.0.jar"
#JVM_OPTIONS+=" -XX:+IdleTuningGcOnIdle";
#JVM_OPTIONS+=" -Xms10m";
#JVM_OPTIONS+=" -Xmx2048m";
#JVM_OPTIONS+=" -Xrs";
#JVM_OPTIONS+=" -Xcheck:jni";

#echo $JVM_OPTIONS

echo oss
LD_LIBRARY_PATH=../../../../deps/openj9-openjdk-jdk14/build/linux-x86_64-server-release/jdk/lib/server/ RLTest --module ../../../redisgears.so --module-args "PluginsDirectory ../../ JvmOptions $JVM_OPTIONS" --clear-logs "$@"

echo cluster 1 shard
LD_LIBRARY_PATH=../../../../deps/openj9-openjdk-jdk14/build/linux-x86_64-server-release/jdk/lib/server/ RLTest --module ../../../redisgears.so --module-args "PluginsDirectory ../../ JvmOptions $JVM_OPTIONS" --clear-logs --env oss-cluster --shards-count 1 "$@"

echo cluster 2 shards
LD_LIBRARY_PATH=../../../../deps/openj9-openjdk-jdk14/build/linux-x86_64-server-release/jdk/lib/server/ RLTest --module ../../../redisgears.so --module-args "PluginsDirectory ../../ JvmOptions $JVM_OPTIONS" --clear-logs --env oss-cluster --shards-count 2 "$@"

echo cluster 3 shards
LD_LIBRARY_PATH=../../../../deps/openj9-openjdk-jdk14/build/linux-x86_64-server-release/jdk/lib/server/ RLTest --module ../../../redisgears.so --module-args "PluginsDirectory ../../ JvmOptions $JVM_OPTIONS" --clear-logs --env oss-cluster --shards-count 3 "$@"
