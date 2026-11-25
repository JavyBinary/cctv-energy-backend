import argparse
import asyncio
import time
from sqlalchemy import text

from db.session import async_session_maker

SEED_MARKER = "?seed="


async def seed_bulk(count: int) -> None:
    started = time.perf_counter()
    async with async_session_maker() as session:
        user_count = (await session.execute(text("SELECT COUNT(*) FROM users"))).scalar_one()
        if user_count == 0:
            await session.execute(
                text("INSERT INTO users (username, password) VALUES ('admin', 'password123')")
            )
            await session.commit()

        sql = text(
            """
            WITH creators AS (
                SELECT array_agg(id) AS ids FROM users
            ),
            resolutions AS (
                SELECT ARRAY['Full HD', '2K QHD', 'Super HD', '4K UHD'] AS vals
            ),
            series AS (
                SELECT
                    n,
                    random() AS r_model,
                    random() AS r_power,
                    random() AS r_res,
                    random() AS r_status,
                    random() AS r_creator,
                    random() AS r_age
                FROM generate_series(1, :count) AS n
            )
            INSERT INTO cameras (
                model_name,
                description,
                status,
                image_url,
                video_url,
                power,
                resolution,
                created_at,
                creator_id,
                published_at
            )
            SELECT
                (ARRAY['DS-2CE16D8T', 'DS-2CD2123G0', 'DS-2CD50C5G0', 'DS-2CD2025FWD', 'DS-2CD2343G2', 'DS-2DE4425IW'])
                    [1 + floor(series.r_model * 6)::int] || '-S' || series.n,
                'Демонстрационная модель камеры #' || series.n || ' для нагрузочного тестирования пагинации и индексов БД.',
                CASE WHEN series.r_status < 0.03 THEN 'deleted' ELSE 'published' END,
                '/DefaultImage.jpg?seed=' || series.n,
                '/DefaultVideo.mp4?seed=' || series.n,
                round((2.5 + series.r_power * 12.5)::numeric, 1)::double precision,
                resolutions.vals[1 + floor(series.r_res * 4)::int],
                CURRENT_TIMESTAMP - (series.r_age * INTERVAL '365 days'),
                creators.ids[1 + floor(series.r_creator * cardinality(creators.ids))::int],
                CURRENT_TIMESTAMP
            FROM series
            CROSS JOIN creators
            CROSS JOIN resolutions
            """
        )
        result = await session.execute(sql, {"count": count})
        await session.commit()
        elapsed = time.perf_counter() - started
        print(f"Inserted {result.rowcount} bulk cameras in {elapsed:.2f}s")


async def clean_bulk() -> None:
    async with async_session_maker() as session:
        result = await session.execute(
            text("DELETE FROM cameras WHERE image_url LIKE :pattern"),
            {"pattern": f"%{SEED_MARKER}%"},
        )
        await session.commit()
        print(f"Removed {result.rowcount} bulk seed cameras")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk seed >100k cameras for Index & Pagination lab")
    parser.add_argument("--count", type=int, default=100000, help="Number of rows to insert")
    parser.add_argument("--clean", action="store_true", help="Remove previously generated bulk rows")
    args = parser.parse_args()

    if args.clean:
        await clean_bulk()
    else:
        await seed_bulk(args.count)


if __name__ == "__main__":
    asyncio.run(main())
