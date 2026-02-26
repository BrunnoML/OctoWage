# Deploy — OctoWage v1.0

> Guia completo do deploy na VPS Hostinger (Ubuntu 24.04).
> Atualizado em 2026-02-26 com a arquitetura real em produção.

---

## Arquitetura de Produção

```
Internet → Nginx nativo (porta 80/443) → Docker FastAPI (porta 8000)
```

| Componente | Tecnologia | Onde roda |
|---|---|---|
| App | FastAPI + Uvicorn (2 workers) | Docker container (`octowage-web`) |
| Proxy reverso | Nginx 1.24 | Nativo no Ubuntu (systemd) |
| SSL | Let's Encrypt (Certbot) | Nativo no Ubuntu |
| DNS | Registro.br | octowage.com.br → 187.77.44.185 |

**Por quê Nginx nativo e não no Docker?**
A VPS já tinha Nginx instalado com SSL para outro projeto (`gestao.ceivc.com.br`). Manter o Nginx nativo permite gerenciar múltiplos domínios/projetos pelo mesmo servidor, com Certbot nativo gerenciando todos os certificados.

---

## VPS — Dados do Servidor

| Item | Valor |
|---|---|
| Provedor | Hostinger |
| Hostname | srv1383574.hstgr.cloud |
| SO | Ubuntu 24.04.4 LTS |
| CPU | 1 vCPU |
| RAM | 4 GB |
| Disco | 50 GB SSD |
| IP | 187.77.44.185 |
| IPv6 | 2a02:4780:6e:aff5::1 |
| Localização | Brasil (Campinas) |
| Usuário SSH | deploy |
| Docker | 29.2.1 |
| Docker Compose | v5.1.0 |

---

## Projetos na VPS

| Domínio | Projeto | Porta interna | Status |
|---|---|---|---|
| octowage.com.br | OctoWage (transparência salarial) | 8000 (Docker) | Ativo |
| gestao.ceivc.com.br | Gestão de alunos CEIVC | — | Configurado (SSL ativo) |

---

## Acesso SSH

### Configuração local (~/.ssh/config)

```
Host octowage-vps
    HostName 187.77.44.185
    User deploy
    IdentityFile ~/.ssh/id_ed25519_github
```

### Conectar

```bash
ssh octowage-vps
```

### Chave SSH

- Tipo: ed25519
- E-mail: brunnoml@gmail.com
- Arquivo local: `~/.ssh/id_ed25519_github`
- Adicionada na Hostinger (nome: octowage-vps) e manualmente em `/home/deploy/.ssh/authorized_keys`

---

## Passo a Passo do Deploy (feito em 2026-02-26)

### 1. DNS (Registro.br)

1. Acessar Registro.br → domínio octowage.com.br
2. Configurar endereçamento → Modo Avançado
3. Criar registros:
   - **A** → `octowage.com.br` → `187.77.44.185`
   - **A** → `www.octowage.com.br` → `187.77.44.185`
4. Aguardar propagação (~2h ao mudar para modo avançado)

Verificar: `dig octowage.com.br +short` → deve retornar `187.77.44.185`

### 2. Chave SSH (uma vez)

```bash
# Gerar chave
ssh-keygen -t ed25519 -C "brunnoml@gmail.com" -f ~/.ssh/id_ed25519_github

# Adicionar ao config SSH
echo '
Host octowage-vps
    HostName 187.77.44.185
    User deploy
    IdentityFile ~/.ssh/id_ed25519_github
' >> ~/.ssh/config

# Adicionar chave na VPS (via terminal Hostinger)
# Copiar conteúdo de: cat ~/.ssh/id_ed25519_github.pub
# Colar em: /home/deploy/.ssh/authorized_keys
```

### 3. Preparar VPS

```bash
ssh octowage-vps

# Atualizar sistema
sudo apt update && sudo apt upgrade -y
sudo reboot

# Após reconectar: verificar Docker
docker --version && docker compose version
```

### 4. Clonar repositório

```bash
sudo mkdir -p /opt/octowage && sudo chown deploy:deploy /opt/octowage
git clone https://github.com/BrunnoML/OctoWage.git /opt/octowage
```

### 5. Configurar ambiente

```bash
# Criar .env
cat > /opt/octowage/.env << 'EOF'
ENVIRONMENT=production
APP_NAME=OctoWage
APP_URL=https://octowage.com.br
EOF

# Criar override para desabilitar Nginx/Certbot do Docker
cat > /opt/octowage/docker-compose.override.yml << 'EOF'
services:
  web:
    ports:
      - "127.0.0.1:8000:8000"
  nginx:
    profiles: ["disabled"]
  certbot:
    profiles: ["disabled"]
EOF
```

### 6. Parar Nginx do Docker, usar Nginx nativo

```bash
# O Nginx nativo já existia (gerencia gestao.ceivc.com.br)
# Desabilitamos temporariamente para testar o Docker, depois reativamos:
sudo systemctl enable nginx && sudo systemctl start nginx
```

### 7. Subir aplicação

```bash
cd /opt/octowage && sudo docker compose up -d --build
```

### 8. Configurar Nginx para OctoWage

```bash
sudo tee /etc/nginx/sites-available/octowage.com.br << 'EOF'
server {
    listen 80;
    server_name octowage.com.br www.octowage.com.br;

    location /static/ {
        alias /opt/octowage/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/octowage.com.br /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 9. Gerar SSL (após DNS propagar)

```bash
sudo certbot --nginx -d octowage.com.br -d www.octowage.com.br --email brunnoml@gmail.com --agree-tos --no-eff-email
```

O Certbot modifica automaticamente o arquivo do Nginx para incluir redirecionamento HTTP→HTTPS.

---

## Atualizar (após cada push)

```bash
ssh octowage-vps
cd /opt/octowage
git pull
sudo docker compose up -d --build
```

Ou em uma linha da máquina local:

```bash
ssh octowage-vps 'cd /opt/octowage && git pull && sudo docker compose up -d --build'
```

---

## Comandos úteis

```bash
# Ver logs da aplicação
sudo docker compose logs -f web

# Ver status do container
sudo docker compose ps

# Reiniciar app
sudo docker compose restart web

# Rebuild forçado (sem cache)
sudo docker compose build --no-cache && sudo docker compose up -d

# Ver logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Status do Nginx
sudo systemctl status nginx

# Testar config do Nginx
sudo nginx -t

# Ver certificados SSL
sudo certbot certificates

# Renovar SSL manualmente
sudo certbot renew

# Ver uso de disco
df -h

# Ver uso de memória
free -h

# Ver containers rodando
sudo docker ps
```

---

## Estrutura na VPS

```
/opt/octowage/                    ← Repositório clonado
├── .env                          ← Variáveis de ambiente (NÃO commitado)
├── docker-compose.yml            ← Define serviços Docker
├── docker-compose.override.yml   ← Override local: desabilita Nginx/Certbot Docker
├── Dockerfile                    ← Build da imagem FastAPI
├── app/                          ← Código FastAPI
├── static/                       ← CSS, JS, imagens (servido pelo Nginx nativo)
└── deploy/                       ← Scripts de deploy (referência)

/etc/nginx/sites-available/
├── default                       ← Site padrão Nginx
├── gestao.ceivc.com.br           ← Gestão de alunos CEIVC (SSL ativo)
└── octowage.com.br               ← OctoWage (HTTP, SSL pendente)

/etc/letsencrypt/live/
├── gestao.ceivc.com.br/          ← Certificados SSL do CEIVC
└── octowage.com.br/              ← Será criado após Certbot (passo 9)
```

---

## Segurança

- FastAPI roda com usuário não-root (`octowage`) dentro do container
- Docker expõe porta 8000 apenas em `127.0.0.1` (não acessível externamente)
- Nginx com headers de segurança (HSTS, X-Frame-Options, X-Content-Type-Options) — serão adicionados após SSL
- SSL A+ no SSL Labs (TLS 1.2/1.3 apenas) — após Certbot
- `.env` no `.gitignore` (nunca commitado)
- `docker-compose.override.yml` no `.gitignore` (config local da VPS)
- Health check a cada 30s no container
- Acesso SSH apenas por chave (sem senha para root)

---

## Problemas encontrados e soluções

| Problema | Causa | Solução |
|---|---|---|
| `Permission denied (publickey)` no SSH | Chave não estava no `/home/deploy/.ssh/authorized_keys` | Adicionada manualmente via terminal Hostinger |
| Nginx Docker não subia (`address already in use :80`) | Nginx nativo já ocupava a porta 80 | Usamos Nginx nativo + Docker só para FastAPI |
| Nginx Docker erro `host not found in upstream "web"` | Container web não resolvia no DNS interno do Docker | Resolvido usando Nginx nativo que acessa `127.0.0.1:8000` |
| Certbot falhou (`no valid A records`) | DNS ainda em propagação (zona em transição no Registro.br) | Aguardar propagação e rodar Certbot novamente |
| `listen 443 ssl http2` deprecado | Nginx Alpine mais recente mudou sintaxe | Usar `listen 443 ssl;` + `http2 on;` separados |

---

## Pendências

- [ ] Aguardar DNS propagar e gerar SSL (passo 9)
- [ ] Após SSL: adicionar headers de segurança no Nginx
- [ ] Configurar renovação automática do SSL (`sudo certbot renew --dry-run`)
- [ ] Monitoramento: configurar alertas de uptime

---

*Última atualização: 2026-02-26*
