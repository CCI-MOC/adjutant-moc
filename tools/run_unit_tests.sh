set -e

export ADJUTANT_CONFIG_FILE=`pwd`/conf/adjutant-testing-unit.yaml

if [ -n "$1" ]; then
  TESTS=$1
else
  TESTS=adjutant_moc.tests.unit
fi

adjutant-api test $TESTS
