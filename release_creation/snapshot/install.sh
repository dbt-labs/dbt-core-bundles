rm -rf target
mkdir target

install_env=".target/snapshot-env-$4"
rm -rf $install_env
python -m venv $install_env --system-site-packages
. $install_env/bin/activate
pyenv local $4

pip install -r $1/requirements/$2.requirements.txt \
--no-index  \
--force-reinstall -v \
--find-links ./$3 \
--target ./target/$4
# dbt --version