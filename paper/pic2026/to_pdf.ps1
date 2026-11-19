# outputs live in the local "PIC 2026 camera-ready" folder next to the repo, outside git
$dir = (Resolve-Path (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "..\..\..\PIC 2026 camera-ready")).Path
$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
  $d = $w.Documents.Open("$dir\PIC2026_Paper325_camera_ready.docx", $false, $true)
  "pages: " + $d.ComputeStatistics(2)
  $d.SaveAs2("$dir\PIC2026_Paper325_camera_ready.pdf", 17)
  $d.Close($false)
} finally { $w.Quit() }
