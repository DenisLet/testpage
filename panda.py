import pandas as pd
import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(
    host="127.0.0.1",
    user="postgres",
    password="123456er",
    port="5432",

)

# SQL запрос для вычисления процентилей
sql_query = """
    SELECT league_name, team, 
        PERCENTILE_CONT(0.0) WITHIN GROUP (ORDER BY total_ft) AS _0,
        PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY total_ft) AS _5,
        PERCENTILE_CONT(0.1) WITHIN GROUP (ORDER BY total_ft) AS _10,
        PERCENTILE_CONT(0.15) WITHIN GROUP (ORDER BY total_ft) AS _15,
        PERCENTILE_CONT(0.2) WITHIN GROUP (ORDER BY total_ft) AS _20,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_ft) AS _25,
        PERCENTILE_CONT(0.3) WITHIN GROUP (ORDER BY total_ft) AS _30,
        PERCENTILE_CONT(0.35) WITHIN GROUP (ORDER BY total_ft) AS _35,
        PERCENTILE_CONT(0.4) WITHIN GROUP (ORDER BY total_ft) AS _40,
        PERCENTILE_CONT(0.45) WITHIN GROUP (ORDER BY total_ft) AS _45,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_ft) AS _50,
        PERCENTILE_CONT(0.55) WITHIN GROUP (ORDER BY total_ft) AS _55,
        PERCENTILE_CONT(0.6) WITHIN GROUP (ORDER BY total_ft) AS _60,
        PERCENTILE_CONT(0.65) WITHIN GROUP (ORDER BY total_ft) AS _65,
        PERCENTILE_CONT(0.7) WITHIN GROUP (ORDER BY total_ft) AS _70,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_ft) AS _75,
        PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY total_ft) AS _80,
        PERCENTILE_CONT(0.85) WITHIN GROUP (ORDER BY total_ft) AS _85,
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY total_ft) AS _90,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY total_ft) AS _95,
        PERCENTILE_CONT(1.0) WITHIN GROUP (ORDER BY total_ft) AS _100
    FROM (
        SELECT league_name, team_home AS team, total_ft FROM matches
        UNION ALL
        SELECT league_name, team_away AS team, total_ft FROM matches
    ) AS team_totals
    GROUP BY league_name, team
    ORDER BY league_name, team;
"""

# Загрузка данных в DataFrame
percentiles_df = pd.read_sql_query(sql_query, conn)

# Закрытие соединения с базой данных
conn.close()

# Вывод результатов
print(percentiles_df.to_string())
