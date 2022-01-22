#!/usr/bin/bash

# This is just a recollection of commands, not actually an idempotent script

python3 -m venv .venv
source .venv/bin/activate

mkdir -p data/out

pushd data
# Download CV (you will need to change the URL to one with credentials)
wget -O cv-ca.tar.gz "https://mozilla-common-voice-datasets.s3.dualstack.us-west-2.amazonaws.com/cv-corpus-7.0-2021-07-21/cv-corpus-7.0-2021-07-21-ca.tar.gz?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAQ3GQRTO3O6QYISCA%2F20220121%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220121T220428Z&X-Amz-Expires=43200&X-Amz-Security-Token=FwoGZXIvYXdzEB8aDM5dHTko%2FgYFHYT21yKSBCt1e4ECom9a6Plxw15QMGcgCfBBRw6J8KSw%2BhB5fja1fT95WWwJcCA3HsPl3I6X434Qax8BhGJInxt3PR8Mr8Gm%2FqZ%2Brth%2BBxM3zLi%2BpARHrlfGnEyhA1gigBN3dqCx1P42rRInRIAyXDLJQ7j83IfA5UyMbO7oUHYIvsWREHf0OaFvbSzgWFjFSWOd%2B8IXAmOE8dpAYlgum7KFXIgxI9EoMJaKPMJ9e20mUJPeawpb3c7Dq1Yg7Q76IPNg%2FjFFShrAEzbk79B8F05N7VXOwzfNov6K4mqCE8htmk%2BfAxPx4J4nenOi93IaiUod%2Fpt9mXk26cu1DoY8gT%2BbqLqB2A5b47%2BvMfmNuffArS%2BGUu1HApXDl2nuV3yHjEFeQwowSD2c%2B4BJDrqUcPURCeJAkX8zzQ80xf%2FTH8fgcLKerHFCxO7t2qRoLikJAwSnx6fWp7zKs7196GBtpP4C4ETCzMXbbXYaId%2BtMxURw17GFFqdMtOScTfTqfmfTvumfF7gOg9c4Y%2F03A3kQhIuNVWpkVIHCx2KUcIAqPdLWKqcHHkNXIhmfLvINfmJBCT8tBo%2B1QHynso02wRpy2WEFXpQugngRjQW1%2FT1ieYEn0miDnk5yWr7Hdi8w3udAgHbDMY%2BR5ftoZtcNXtDT2vJ2gtBlbrPgINue79lOtYGLMaSEGNYV%2BfHY7Fmlna02hBXg4jytZZaKIjHrI8GMioyYuLVbCn5%2Bqx55S7GLmSShUw5cn3mI1AnMTG5BYsaOjY1W3lNwH9PJPI%3D&X-Amz-Signature=6db41b241dbf21d6c81505bd157f47a0b5ab38e5401c072cb9537163853278d3&X-Amz-SignedHeaders=host"

# Download ParlamentParla
wget http://laklak.eu/share/clean_train.tar.gz
wget http://laklak.eu/share/other_train.tar.gz
wget http://laklak.eu/share/other_dev.tar.gz
wget http://laklak.eu/share/clean_dev.tar.gz

# Download TV3Parla
wget http://laklak.eu/share/tv3_0.3.tar.gz

popd

# Import data to expected format
python importer_cv.py data/cv-corpus-7.0-2021-07-21/ca --output_dir data/out/
python importer_parlament.py data/ --output_dir data/out/
python importer_tv3.py data/tv3_0.3/wav/ --output_dir data/out/

# Combine CSVs
echo "wav_filename,wav_filesize,transcript" > data/out/eval.csv
for i in "clean_dev_parlament.csv" "other_dev_parlament.csv" "dev_cv.csv"; do
    sed -n '2,$p' data/out/$i >> data/out/eval.csv
done;

echo "wav_filename,wav_filesize,transcript" > data/out/train.csv
for i in "clean_train_parlament.csv" "other_train_parlament.csv" "train_cv.csv" "train_tv3.csv"; do
    sed -n '2,$p' data/out/$i >> data/out/train.csv
done;