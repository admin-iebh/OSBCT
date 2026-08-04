set -e
R=/sessions/rcw-01bcgpjfpcgbdwzs1dqi2qk7/mnt/OSBCT
V=$1
FILES="site/$V.json site/reader/verse/$V.json site/reader/sections/$V.json site/reader/uddana/$V.json site/reader/hide/$V.json site/reader/incipit/$V.json site/reader/booktitle/$V.json site/reader/bold/$V.bold.json"
case $2 in
 pre)  for f in $FILES; do [ -e "$R/$f.prereseg2" ] && mv "$R/$f" "$R/$f.POST" && cp "$R/$f.prereseg2" "$R/$f"; done;;
 post) for f in $FILES; do [ -e "$R/$f.POST" ] && mv "$R/$f.POST" "$R/$f"; done;;
esac
echo "$V -> $2"
