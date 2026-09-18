
rm *.xz

for i in *.png; do
convert $i -color-matrix '0 0 1 0 1 0 1 0 0' rgba:$(basename $i .png).raw
xz $(basename $i .png).raw
done;
