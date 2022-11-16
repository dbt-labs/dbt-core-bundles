rm -rf target
mkdir target
pip install -r $1/requirements/$2.requirements.txt \
--no-index  \
--force-reinstall \
--find-links ./tmp/ \
--target ./target