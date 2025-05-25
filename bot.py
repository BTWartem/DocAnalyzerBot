from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from utils.file_parser import parse_file
from utils.embeddings import create_vector_db, load_vector_db
from utils.llm import generate_answer
from config import BOT_TOKEN, DOCUMENTS_DIR, doc_manager
import os


async def handle_document(update: Update, context):
    if not update.message or not update.message.document:
        return

    file = await update.message.document.get_file()
    doc_name = update.message.document.file_name
    file_path = os.path.join(DOCUMENTS_DIR, doc_name)

    try:
        await file.download_to_drive(file_path)
        text = parse_file(file_path)

        # Проверка содержания
        if len(text) < 100:
            raise ValueError("Документ слишком короткий или нечитаем")

        create_vector_db(text, doc_name)
        doc_manager.set_current(doc_name)

        # Адаптивное сообщение
        doc_type = "Конституция РФ" if "конституция" in doc_name.lower() else "документ"
        await update.message.reply_text(
            f"📄 {doc_type} '{doc_name}' успешно загружен!\n"
            f"Теперь вы можете задавать вопросы о его содержании."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка загрузки: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)


async def handle_question(update: Update, context):
    if not update.message:
        return

    current_doc = doc_manager.get_current()
    if not current_doc:
        await update.message.reply_text("❌ Нет активного документа. Загрузите файл сначала.")
        return

    try:
        # Добавляем проверку типа документа
        if "конституция" in current_doc.lower():
            system_note = "\nЭто юридический документ высшей юридической силы."
        else:
            system_note = ""

        db = load_vector_db(current_doc)
        docs = db.similarity_search(update.message.text, k=2)
        context_text = "\n".join([doc.page_content for doc in docs]) + system_note

        answer = generate_answer(update.message.text, context_text)
        await update.message.reply_text(answer[:4000])  # Обрезаем слишком длинные ответы
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка обработки: {str(e)}")

async def list_docs(update: Update, context):
    """Показать список загруженных документов"""
    docs = "\n".join(doc_manager.loaded_docs.keys()) or "Нет загруженных документов"
    current = doc_manager.get_current() or "Не выбран"
    await update.message.reply_text(
        f"📂 Загруженные документы:\n{docs}\n\n"
        f"Текущий документ: {current}"
    )


async def switch_doc(update: Update, context):
    """Переключение между документами"""
    if not context.args:
        await update.message.reply_text("Укажите название документа: /switch <имя_файла>")
        return

    doc_name = " ".join(context.args)
    try:
        if doc_name not in doc_manager.loaded_docs:
            raise ValueError("Документ не найден")

        doc_manager.set_current(doc_name)
        await update.message.reply_text(f"✅ Текущий документ изменен на: {doc_name}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Обработчики сообщений
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    # Обработчики команд
    app.add_handler(CommandHandler("list", list_docs))
    app.add_handler(CommandHandler("switch", switch_doc))

    app.run_polling()


if __name__ == "__main__":
    main()