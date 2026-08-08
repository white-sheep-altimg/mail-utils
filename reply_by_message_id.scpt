on run argv
	if (count of argv) < 1 then
		display dialog "使い方: osascript reply_by_message_id.scpt 'Message-ID' '本文'" buttons {"OK"} default button "OK"
		return
	end if

	set targetMessageID to item 1 of argv

	if (count of argv) ≥ 2 then
		set fixedReplyText to item 2 of argv
	else
		set fixedReplyText to "ご連絡ありがとうございます。" & return & "確認いたしました。よろしくお願いいたします。"
	end if

	set normalizedTargetID to my normalizeMessageID(targetMessageID)

	tell application "Mail"
		set targetMessage to missing value

		repeat with ac in every account
			repeat with mb in every mailbox of ac
				try
					repeat with msg in (every message of mb)
						set currentID to my normalizeMessageID(message id of msg)
						if currentID is normalizedTargetID then
							set targetMessage to contents of msg
							exit repeat
						end if
					end repeat
				end try

				if targetMessage is not missing value then exit repeat
			end repeat

			if targetMessage is not missing value then exit repeat
		end repeat

		if targetMessage is missing value then
			display dialog "指定したMessage-IDのメールが見つかりませんでした。" buttons {"OK"} default button "OK"
			return
		end if

		activate
		reply targetMessage with opening window
	end tell

	delay 1.5

	set the clipboard to fixedReplyText & return & return

	tell application "System Events"
		tell process "Mail"
			keystroke "v" using command down
		end tell
	end tell

	delay 0.3

	tell application "Mail"
		send front outgoing message
	end tell
end run

on normalizeMessageID(theID)
	set s to theID as text
	set s to my replaceText("<", "", s)
	set s to my replaceText(">", "", s)
	set s to my replaceText(" ", "", s)
	return s
end normalizeMessageID

on replaceText(findText, replaceWith, sourceText)
	set AppleScript's text item delimiters to findText
	set textItems to every text item of sourceText
	set AppleScript's text item delimiters to replaceWith
	set newText to textItems as text
	set AppleScript's text item delimiters to ""
	return newText
end replaceText
