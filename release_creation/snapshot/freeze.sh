set -e
pip freeze --path ./target/$2 > $1
sed -i "" "s/dbt-core==.*/& --no-binary dbt-postgres/g" $1