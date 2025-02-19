sh '''
cp .env.example .env
sed -i 's/^DB_HOST=.*/DB_HOST=localhost/' .env
sed -i 's/^DB_HOST_RO=.*/DB_HOST_RO=localhost/' .env
sed -i 's/^DB_SCHEMA=.*/DB_SCHEMA=spillman_automation/' .env
sed -i 's/^DB_USER=.*/DB_USER=root/' .env
sed -i 's/^DB_PASSWORD=.*/DB_PASSWORD=/' .env
'''