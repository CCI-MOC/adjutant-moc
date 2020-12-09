set -e

export ADJUTANT_CONFIG_FILE=`pwd`/conf/adjutant-testing-functional.yaml
sed -i -e "
        s|%OPENSTACK_PASSWORD%|$OS_PASSWORD|g;
" conf/adjutant-testing-functional.yaml

if [ -n "$1" ]; then
  TESTS=$1
else
  TESTS=adjutant_moc.tests.functional
fi

adjutant-api test $TESTS
