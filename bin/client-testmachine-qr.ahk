
SysGet, no_of_monitors, MonitorCount
Loop, %no_of_monitors%
{
	Random, rand_no, 1, 1000
	file=%temp%\%rand_no%qr.bmp
	SysGet, CurrMon, Monitor, %A_Index%
	col:= Abs(CurrMonLeft-CurrMonRight)
	row:= Abs(CurrMonTop-CurrMonBottom)
	qr_size:= col > row ? row : col
	Run, qrcode.exe -o %file% -s 256 %A_Index%_%CurrMonLeft%_%CurrMonTop%_%col%_%row%
	OutputVar = 0
	while OutputVar < 70000
	{
		FileGetSize, OutputVar, %file%
		sleep 100
	}
		
	win_name:= %A_Index%_%CurrMonLeft%_%CurrMonTop%
	Gui, New, +ToolWindow +AlwaysOnTop -SysMenu -Border, %win_name%
	Gui, Color, FFFFFF
	Gui, Add, Picture,vQr w%qr_size% h%qr_size%, %file%
	Gui,Show,x%CurrMonLeft% y%CurrMonTop% w%col% h%row% Maximize, %win_name%
	
	GuiControlGet, Pic, Pos, Qr
	xx := (col-picw)/2
	yy := (row-pich)/2
	GuiControl, MoveDraw, Qr, x%xx% y%yy%
	WinSet,Transparent,0 ,%win_name%
	FileDelete, file
	
		
		
}
Sleep, 9999999
send, {Esc}

Escape::
ExitApp
Return
