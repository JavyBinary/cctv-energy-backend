-- ============================================================================
-- Скрипт на языке Lua для СУБД Redis (Лабораторная работа №4, Лекция 6, слайд 10)
-- Назначение: получение списка активных сессий пользователей и соответствующих user_id
-- Запуск через redis-cli:
--   redis-cli --eval app/scripts/get_active_sessions.lua
-- Или из терминала контейнера:
--   docker exec -i redis redis-cli --eval - < app/scripts/get_active_sessions.lua
-- ============================================================================

local session_keys = redis.call('keys', 'session:*')
local active_sessions = {}

for index, session_key in ipairs(session_keys) do
    local user_id = redis.call('get', session_key)
    table.insert(active_sessions, session_key .. ' -> user_id: ' .. tostring(user_id))
end

return active_sessions
