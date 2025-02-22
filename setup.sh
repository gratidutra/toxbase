# Cria a rede selenoid (se não existir)
docker network create selenoid 

# Puxa as imagens necessárias
docker pull selenoid/chrome:127.0
docker pull selenoid/firefox:124.0