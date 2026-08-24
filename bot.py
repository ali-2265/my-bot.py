async def handle_show_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle showing original text in popup when button is clicked."""
    query = update.callback_query
    callback_data = query.data
    user_id = query.from_user.id
    
    logger.info("========== BUTTON CLICK ==========")
    logger.info(f"Callback data: {repr(callback_data)}")
    logger.info(f"User ID: {user_id}")
    
    try:
        if not callback_data.startswith("show_"):
            logger.warning(f"Invalid callback format: {callback_data}")
            await query.answer("❌ دستور نامعتبر.", show_alert=True)
            return
        
        unique_id = callback_data[5:]
        logger.info(f"Extracted text ID: {unique_id}")
        
        text_data = await get_text_content(unique_id)
        
        if text_data and text_data.get("original_text"):
            original_text = text_data["original_text"]
            logger.info(f"Original text length: {len(original_text)}")
            
            # ========== شروع تغییرات ==========
            # 1. دریافت نام کانال
            channel_name = await get_channel_name(context)
            
            # 2. حذف خطوط جداکننده از متن
            cleaned_text = original_text
            # حذف از ابتدا
            while cleaned_text.startswith("----------------------------------") or cleaned_text.startswith("_------------------------"):
                cleaned_text = cleaned_text[len("----------------------------------"):].lstrip()
            # حذف از انتها
            while cleaned_text.endswith("----------------------------------") or cleaned_text.endswith("_------------------------"):
                cleaned_text = cleaned_text[:-len("----------------------------------")].rstrip()
            # حذف خطوط جداکننده در بین متن
            lines = cleaned_text.split('\n')
            filtered_lines = []
            for line in lines:
                if line.strip() != "----------------------------------" and line.strip() != "_------------------------":
                    filtered_lines.append(line)
            cleaned_text = '\n'.join(filtered_lines).strip()
            
            # 3. ساخت متن نهایی - نام کانال در سمت راست و بزرگ‌تر
            # استفاده از فاصله‌های زیاد برای قرار گرفتن در سمت راست
            display_text = f"{' ' * 40}{channel_name}\n\n{cleaned_text}"
            
            # 4. ارسال متن به PV کاربر
            try:
                # ارسال متن به کاربر
                await context.bot.send_message(
                    chat_id=user_id,
                    text=display_text
                )
                logger.info(f"Text sent to PV of user {user_id}")
                
                # 5. ارسال پیام موفقیت
                await context.bot.send_message(
                    chat_id=user_id,
                    text="✅ متن با موفقیت ارسال شد"
                )
                logger.info(f"Success message sent to PV of user {user_id}")
                
                # پاسخ به کلیک دکمه
                await query.answer("✅ متن برای شما ارسال شد.", show_alert=False)
                
            except TelegramError as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                await query.answer("❌ خطا در ارسال متن. لطفاً دوباره تلاش کنید.", show_alert=True)
            # ========== پایان تغییرات ==========
            
        else:
            logger.error("Original text not found")
            await query.answer("❌ متن یافت نشد.", show_alert=True)
            
    except Exception as e:
        logger.exception(f"Error in handle_show_text: {e}")
        await query.answer("❌ خطا در نمایش متن.", show_alert=True)
