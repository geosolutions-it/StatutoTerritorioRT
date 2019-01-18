echo "Killing processes..."
ps -efl | grep runserver
pkill -9 -f "runserver" -e
echo "... check"
ps -efl | grep runserver
