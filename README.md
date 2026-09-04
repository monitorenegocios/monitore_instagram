# Monitore — Página de links para Instagram

## Estrutura

- `index.html` — página principal.
- `assets/logo-branca.png` — logo original da Monitore em branco.
- `data/posts.json` — dados das 6 últimas publicações.
- `scripts/update_blog.py` — lê o RSS do Blog Wix e atualiza títulos, links, datas e imagens.
- `.github/workflows/update-blog.yml` — executa a atualização automaticamente a cada 6 horas.

## Como colocar no GitHub Pages

1. Crie um repositório no GitHub, por exemplo `monitore-instagram`.
2. Envie **todo o conteúdo desta pasta**, mantendo as pastas `assets`, `data`, `scripts` e `.github`.
3. No GitHub, vá em **Settings → Pages**.
4. Em **Build and deployment**, selecione **Deploy from a branch**.
5. Selecione a branch `main` e a pasta `/ (root)`.
6. Salve e aguarde o GitHub publicar a página.
7. O endereço será parecido com:
   `https://SEU-USUARIO.github.io/monitore-instagram/`

## Atualização automática do Blog

O Blog da Monitore é Wix. O Wix disponibiliza um feed RSS para o blog no formato `/blog-feed.xml`.

O workflow consulta esse feed a cada 6 horas, pega as 6 publicações mais recentes e tenta localizar a imagem de capa original no RSS. O resultado é salvo em `data/posts.json`.

Quando houver uma nova publicação, o workflow atualiza o JSON e faz o commit automaticamente. A página do GitHub Pages passa a mostrar o novo conjunto de 6 posts.

Também é possível executar manualmente em:

**Actions → Atualizar Blog da Monitore → Run workflow**

## Importante sobre as imagens

A página não usa capas criadas artificialmente. O atualizador tenta usar a imagem real publicada no artigo do Blog da Monitore. Isso é mais confiável do que tentar buscar a imagem diretamente no navegador, pois evita problemas de CORS.

Se o RSS do Wix não expuser a imagem de uma publicação, o card continua funcionando com uma área de fallback; título e link permanecem disponíveis.

## Links configurados

- Site: https://www.monitorenegocios.com.br/
- LinkedIn: https://www.linkedin.com/company/monitorenegocios/
- WhatsApp: 98 92001-0615
- Diagnóstico: https://monitorenegocios.github.io/diagnostico_mne/
- Blog: https://www.monitorenegocios.com.br/blogs/
