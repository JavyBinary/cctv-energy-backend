#!/usr/bin/env bash
# Скрипт для демонстрации содержимого Redis и выполнения Lua-скрипта из лекции 6
# Запуск: bash scripts/redis_sessions.sh

echo "=========================================="
echo " 1. Проверка всех ключей сессий в Redis:"
echo "=========================================="
if command -v redis-cli &> /dev/null; then
    redis-cli keys "session:*"
elif docker ps --format '{{.Names}}' | grep -q "redis_cache"; then
    docker exec -it redis_cache redis-cli keys "session:*"
else
    echo "Redis CLI / контейнер недоступен напрямую. Проверьте docker-compose."
fi

echo ""
echo "=========================================="
echo " 2. Lua-скрипт из лекции (активные сессии и user_id):"
echo "=========================================="
LUA_SCRIPT="local keys = redis.call('keys', 'session:*'); local res = {}; for i, k in ipairs(keys) do res[i] = k .. ' -> user_id:' .. tostring(redis.call('get', k)) end; return res;"

if command -v redis-cli &> /dev/null; then
    redis-cli EVAL "$LUA_SCRIPT" 0
elif docker ps --format '{{.Names}}' | grep -q "redis_cache"; then
    docker exec -it redis_cache redis-cli EVAL "$LUA_SCRIPT" 0
fi

echo ""
echo "=========================================="
echo " 3. Информация о клиентах (CLIENT LIST):"
echo "=========================================="
if command -v redis-cli &> /dev/null; then
    redis-cli CLIENT LIST
elif docker ps --format '{{.Names}}' | grep -q "redis_cache"; then
    docker exec -it redis_cache redis-cli CLIENT LIST
fi
