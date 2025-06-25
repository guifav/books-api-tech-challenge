#!/bin/bash
# Script para testar todos os endpoints da API

echo "🧪 Testando Books API..."
echo "================================"

BASE_URL="http://localhost:5005"

echo "1️⃣  Testando Health Check..."
curl -s "$BASE_URL/api/v1/health" | python -m json.tool
echo -e "\n"

echo "2️⃣  Testando página inicial..."
curl -s "$BASE_URL/" | python -m json.tool
echo -e "\n"

echo "3️⃣  Testando lista de livros (primeiros 3)..."
curl -s "$BASE_URL/api/v1/books" | python -m json.tool | head -50
echo -e "\n"

echo "4️⃣  Testando livro específico (ID 1)..."
curl -s "$BASE_URL/api/v1/books/1" | python -m json.tool
echo -e "\n"

echo "5️⃣  Testando busca por título..."
curl -s "$BASE_URL/api/v1/books/search?title=book" | python -m json.tool | head -30
echo -e "\n"

echo "6️⃣  Testando lista de categorias..."
curl -s "$BASE_URL/api/v1/categories" | python -m json.tool
echo -e "\n"

echo "7️⃣  Testando estatísticas gerais..."
curl -s "$BASE_URL/api/v1/stats/overview" | python -m json.tool
echo -e "\n"

echo "8️⃣  Testando livros mais bem avaliados..."
curl -s "$BASE_URL/api/v1/books/top-rated" | python -m json.tool | head -30
echo -e "\n"

echo "9️⃣  Testando filtro por preço..."
curl -s "$BASE_URL/api/v1/books/price-range?min=10&max=30" | python -m json.tool | head -30
echo -e "\n"

echo "🔟 Testando endpoint inexistente (deve retornar 404)..."
curl -s -w "Status: %{http_code}\n" "$BASE_URL/api/v1/nonexistent"
echo -e "\n"

echo "✅ Teste concluído!"