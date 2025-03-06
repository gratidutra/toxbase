.PHONY: setup build up down clean

# Configuração inicial
setup:
	@echo "Criando a rede 'selenoid' caso não exista..."
	@docker network ls | grep -q "selenoid" || docker network create selenoid
	@echo "Baixando imagens do Selenoid..."
	@docker pull selenoid/chrome:127.0
	@docker pull selenoid/firefox:124.0
	@echo "Setup concluído!"

# Builda a aplicação
build:
	@echo "Construindo os containers..."
	@docker compose up --build
	@echo "Build concluído!"

# Sobe a aplicação
up: setup build
	@echo "Iniciando os containers..."
	@docker compose up -d
	@echo "Aplicação rodando!"

# Derruba os containers
down:
	@echo "Derrubando os containers..."
	@docker compose down

# Remove containers, imagens não utilizadas e a rede
clean: down
	@echo "Removendo imagens não utilizadas..."
	@docker system prune -f
	@echo "Removendo a rede 'selenoid'..."
	@docker network rm selenoid || true
	@echo "Cleanup concluído!"
