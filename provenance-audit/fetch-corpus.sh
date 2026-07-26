#!/bin/bash
# Download the reference implementations' source jars from Maven Central and unpack them
# per specification family. Central only — no binary from anywhere else is involved.
#
# Usage: bash provenance-audit/fetch-corpus.sh
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RI=$HERE/ri
CORPUS=$HERE/corpus
mkdir -p "$RI"

get() { # groupId artifactId version label
  local g=$1 a=$2 v=$3 l=$4 p
  p=$(echo "$g" | tr '.' '/')
  if [ -f "$RI/$a-$v-sources.jar" ]; then
    printf "%-36s %-14s (déjà présent)\n" "$l" "$v"; return
  fi
  if curl -sfL -o "$RI/$a-$v-sources.jar" \
      "https://repo1.maven.org/maven2/$p/$a/$v/$a-$v-sources.jar"; then
    printf "%-36s %-14s %s Ko\n" "$l" "$v" "$(( $(wc -c < "$RI/$a-$v-sources.jar") / 1024 ))"
  else
    rm -f "$RI/$a-$v-sources.jar"
    printf "%-36s %-14s ECHEC\n" "$l" "$v"
  fi
}

echo "=== Téléchargement des implémentations de référence ==="
printf "%-36s %-14s %s\n" "ARTEFACT" "VERSION" "TAILLE"
# CDI
get org.jboss.weld weld-core-impl 5.1.2.Final          "Weld 5 (CDI 4.0)"
get org.jboss.weld weld-core-impl 6.0.3.Final          "Weld 6 (CDI 4.1)"
get org.jboss.weld weld-core-impl 7.0.0.Beta2          "Weld 7"
# JSON
get org.eclipse.parsson parsson 1.1.9                  "Parsson (JSON-P)"
get org.eclipse yasson 3.0.4                           "Yasson (JSON-B)"
# JAX-RS
get org.glassfish.jersey.core jersey-server 3.1.9      "Jersey 3.1 server"
get org.glassfish.jersey.core jersey-common 3.1.9      "Jersey 3.1 common"
get org.glassfish.jersey.core jersey-server 5.0.0-M1   "Jersey 5 server"
get org.glassfish.jersey.core jersey-common 5.0.0-M1   "Jersey 5 common"
# Servlet
get org.apache.tomcat tomcat-catalina 10.1.34          "Tomcat 10.1 catalina"
get org.apache.tomcat tomcat-catalina 11.0.24          "Tomcat 11 catalina"
get org.eclipse.jetty jetty-server 12.0.16             "Jetty 12 server"
# HTTP
get io.netty netty-codec-http 4.1.115.Final            "Netty 4.1 HTTP/1"
get io.netty netty-codec-http2 4.1.115.Final           "Netty 4.1 HTTP/2"
get io.netty netty-codec-http 5.0.0.Alpha2             "Netty 5 HTTP/1"
get io.netty netty-codec-http2 5.0.0.Alpha2            "Netty 5 HTTP/2"
# MicroProfile
get io.smallrye.config smallrye-config-core 3.18.1     "SmallRye Config"
get io.smallrye smallrye-health 4.3.0                  "SmallRye Health"
get io.smallrye smallrye-metrics 5.1.0                 "SmallRye Metrics"
get io.smallrye smallrye-fault-tolerance 7.0.0-RC1     "SmallRye Fault Tolerance"
get io.smallrye smallrye-open-api-core 4.4.0-alpha1    "SmallRye OpenAPI"
get io.smallrye smallrye-jwt 5.0.0-RC2                 "SmallRye JWT"
get org.jboss.resteasy.microprofile microprofile-rest-client 3.0.1.Final "RESTEasy MP Rest Client"
# Persistence
get org.hibernate.orm hibernate-core 8.0.0.Beta1       "Hibernate ORM"

echo
echo "=== Dépliage par famille de spécification ==="
rm -rf "$CORPUS"; mkdir -p "$CORPUS"
unpack() { # family regex...
  local fam=$1; shift
  local d=$CORPUS/$fam; mkdir -p "$d"
  for pat in "$@"; do
    for j in $(ls -1 "$RI" 2>/dev/null | grep -E "$pat"); do
      # One sub-directory per jar: several versions of the same implementation share their
      # class paths, so unpacking them together would let the last one overwrite the others
      # and silently reduce the corpus to a single version.
      local sub="$d/${j%-sources.jar}"; mkdir -p "$sub"
      (cd "$sub" && unzip -qo "$RI/$j" '*.java' 2>/dev/null)
    done
  done
  printf "%-12s %6s fichiers .java\n" "$fam" "$(find "$d" -name '*.java' | wc -l | tr -d ' ')"
}
unpack cdi       "^weld-core-impl"
unpack json      "^parsson|^yasson"
unpack jaxrs     "^jersey-"
unpack servlet   "^tomcat-catalina|^jetty-server"
unpack http      "^netty-codec-http"
unpack mpconfig  "^smallrye-config"
unpack mphealth  "^smallrye-health"
unpack mpmetrics "^smallrye-metrics"
unpack mpft      "^smallrye-fault"
unpack mpopenapi "^smallrye-open-api"
unpack mpjwt     "^smallrye-jwt"
unpack mprest    "^microprofile-rest-client"
unpack jpa       "^hibernate-core"
echo "---"
echo "TOTAL corpus de référence: $(find "$CORPUS" -name '*.java' | wc -l | tr -d ' ') fichiers"
