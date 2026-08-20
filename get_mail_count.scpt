tell application "Mail"
  set unreadTotal to 0

  repeat with ac in every account
    repeat with mb in every mailbox of ac
      try
	set mbName to name of mb
	if mbName is "Inbox" or mbName is "INBOX" or mbName is "受信" then
	  set unreadTotal to unreadTotal + (count of (every message of mb whose read status is false))
	end if
      end try
    end repeat
  end repeat

  return unreadTotal
end tell
