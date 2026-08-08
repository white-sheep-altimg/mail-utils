on run argv
	if (count of argv) < 4 then
		display dialog "使い方: osascript send_mail.scpt 'From' 'To' 'Subject' '本文'" buttons {"OK"} default button "OK"
		return
	end if

  set theSender to item 1 of argv
  set recipientAddress to item 2 of argv
  set recipientName to item 2 of argv
  set theSubject to item 3 of argv
  set theContent to item 4 of argv

  tell application "Mail"
      set theMessage to make new outgoing message with properties {subject:theSubject, content:theContent & return, sender:theSender, visible:true}
      tell theMessage
          make new to recipient with properties {name:recipientName, address:recipientAddress}
      end tell
  end tell
end run
