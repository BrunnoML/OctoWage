# Deploy — OctoWage v1.0

> Guia passo a passo para deploy na VPS Hostinger (Ubuntu 24.04).

---

## Pré-requisitos

- VPS com Ubuntu 24.04 LTS
- Acesso SSH como root
- Domínio `octowage.com.br` apontando para o IP da VPS
- Repositório no GitHub: `github.com/BrunnoML/octowage`

## Infraestrutura

| Componente | Tecnologia | Porta |
|---|---|---|
| App | FastAPI + Uvicorn (2 workers) | 8000 (interna) |
| Proxy | Nginx (reverse proxy + SSL) | 80, 443 |
| SSL | Let's Encrypt (Certbot) | auto-renew |
| Container | Docker + Docker Compose | — |

## Passo 1 — Configurar DNS

No painel do Registro.br (ou onde registrou o domínio):

1. Criar registro **A** apontando `octowage.com.br` → `187.77.44.185`
2. Criar registro **A** apontando `www.octowage.com.br` → `187.77.44.185`
3. Aguardar propagação (até 24h, geralmente minutos)

Verificar: `dig octowage.com.br` deve retornar `187.77.44.185`.

## Passo 2 — Setup da VPS (uma vez)

Da sua máquina local:

```bash
ssh root@187.77.44.185 'bash -s' < deploy/setup-vps.sh
```

O script instala: Docker, Docker Compose, Git, clona o repo em `/opt/octowage` e cria o `.env`.

## Passo 3 — Primeiro deploy

```bash
ssh root@187.77.44.185
cd /opt/octowage
bash deploy/start.sh
```

O script:
1. Verifica se o DNS aponta corretamente
2. Sobe Nginx temporário (HTTP)
3. Gera certificado SSL via Let's Encrypt
4. Reinicia tudo com HTTPS

Acesse: `https://octowage.com.br`

## Atualizar (após cada push)

Opção 1 — Da sua máquina:
```bash
ssh root@187.77.44.185 'cd /opt/octowage && bash deploy/update.sh'
```

Opção 2 — Logado na VPS:
```bash
cd /opt/octowage
bash deploy/update.sh
```

O script faz: `git pull` → `docker compose up -d --build` → limpa imagens antigas.

## Comandos úteis

```bash
# Ver logs da aplicação
docker compose logs -f web

# Ver logs do Nginx
docker compose logs -f nginx

# Ver status dos containers
docker compose ps

# Reiniciar tudo
docker compose restart

# Parar tudo
docker compose down

# Rebuild forçado (sem cache)
docker compose build --no-cache && docker compose up -d
```

## Renovação do SSL

O Certbot renova automaticamente a cada 12 horas (container `certbot`). Não precisa fazer nada manualmente.

Para forçar renovação:
```bash
docker compose run --rm certbot renew --force-renewal
docker compose restart nginx
```

## Estrutura na VPS

```
/opt/octowage/
├── .env                  ← Variáveis de ambiente (NÃO commitar)
├── Dockerfile
├── docker-compose.yml
├── deploy/
│   ├── nginx.conf        ← Config do Nginx
│   ├── setup-vps.sh      ← Setup inicial (1x)
│   ├── start.sh          ← Primeiro deploy (1x)
│   └── update.sh         ← Atualizar (cada push)
├── app/                  ← Código FastAPI
└── static/               ← CSS, JS, imagens
```

## Segurança

- FastAPI roda com usuário não-root (`octowage`) dentro do container
- Nginx com headers de segurança (HSTS, X-Frame-Options, X-Content-Type-Options)
- SSL A+ no SSL Labs (TLS 1.2/1.3 apenas)
- `.env` no `.gitignore` (nunca commitado)
- Health check a cada 30s no container

## Convivência com outros projetos

A VPS pode hospedar múltiplos projetos. Cada projeto usa sua própria rede Docker e porta interna. O Nginx faz o roteamento por domínio:
- `octowage.com.br` → container `octowage-web:8000`
- `outroprojeto.com.br` → container `outroprojeto:XXXX`

Para adicionar outro projeto, basta criar outro `server {}` block no Nginx ou usar um Nginx externo compartilhado.

---

*Última atualização: 2026-02-26*
