
SysGet, no_of_monitors, MonitorCount
Loop, %no_of_monitors%
{
	SysGet, CurrMon, Monitor, %A_Index%
	win_name:= A_Index . "_" .  CurrMonLeft . "_" .  CurrMonTop
	Gui, New, -Border -SysMenu -Caption
	Gui, Color, 000000
	Sleep,10
	ScreenWidth := A_ScreenWidth 
	ScreenHeight:= A_ScreenHeight
	Gui,Show,x%CurrMonLeft% y%CurrMonTop%  w%ScreenWidth% h%ScreenHeight% Maximize, %win_name%

	
}
Sleep, 99999
send, {Esc}

Escape::
ExitApp
Return
