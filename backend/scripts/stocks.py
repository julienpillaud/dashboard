# import asyncio
# import logging
# from pathlib import Path
#
# import openpyxl
#
# from app.domain.categories.use_cases import get_categories
# from scripts.commons import get_context, get_stores, setup_logging
#
# logger = logging.getLogger("app.stocks")
# project_path = Path(__file__).parents[1]
#
#
# async def main() -> None:
#     setup_logging(project_path)
#     context = await get_context()
#     stores = await get_stores(context)
#     store = next(iter(store for store in stores if store.slug == "pessac"))
#     pos_manager = context.get_pos_manager(store=store)
#     raw_articles = await pos_manager.get_articles(limit=3000)
#
#     categories = await get_categories(context, store_slug=store.slug)
#     categories_map = {category.raw.id: category for category in categories.items}
#
#     wb = openpyxl.Workbook()
#     ws = wb.active
#     ws.append(
#         [
#             "ID article\nNe pas modifier",
#             "ID déclinaison\nNe pas modifier",
#             "CatégorieNe pas modifier",
#             "Nom de l'article\nNe pas modifier",
#             "Déclinaison\nNe pas modifier",
#             "Référence\nNe pas modifier",
#             "Code-barres\nNe pas modifier",
#             "Quantité du mouvement\nA entrer ou sortir du stock",
#         ]
#     )
#
#     for raw_article in raw_articles:
#         category = categories_map[raw_article.category_id]
#
#         if raw_article.stock_quantity is None or raw_article.stock_quantity <= 0:
#             continue
#
#         ws.append(
#             [
#                 raw_article.id,
#                 "",
#                 category.raw.name,
#                 raw_article.name,
#                 "",
#                 raw_article.reference,
#                 raw_article.barcode,
#                 raw_article.stock_quantity,
#             ]
#         )
#
#     wb.save("movement.xlsx")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
