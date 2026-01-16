param(
  [string]$Root = "C:\g7core\g7_v1"
)

$ErrorActionPreference = "Stop"

function Write-Utf8NoBom([string]$Path, [string]$Text) {
  $enc = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Text, $enc)
}

$gptDir = Join-Path $Root "GPTORDER"
$engDir = Join-Path $Root "engine"
New-Item -ItemType Directory -Force -Path $gptDir | Out-Null
New-Item -ItemType Directory -Force -Path $engDir | Out-Null

$smokePath = Join-Path $gptDir "SMOKE3.txt"
$aPath     = Join-Path $gptDir "REAL120_A.txt"
$bPath     = Join-Path $gptDir "REAL120_B.txt"
$catPath   = Join-Path $engDir "work_catalog_v2.json"

function Make-Ids([string]$prefix, [int]$n) {
  $ids = @()
  for ($i=1; $i -le $n; $i++) {
    $ids += ("{0}{1:d3}" -f $prefix, $i)
  }
  return $ids
}

$A = Make-Ids "box01_half1_seq" 120
$B = Make-Ids "box01_half2_seq" 120

$smoke = @()
$smoke += ("TASK_V2|payload={0}" -f $A[0])
$smoke += ("TASK_V2|payload={0}" -f $A[1])
$smoke += ("TASK_V2|payload={0}" -f $A[2])
Write-Utf8NoBom $smokePath ($smoke -join "`n")

Write-Utf8NoBom $aPath (($A | ForEach-Object { "TASK_V2|payload=$_" }) -join "`n")
Write-Utf8NoBom $bPath (($B | ForEach-Object { "TASK_V2|payload=$_" }) -join "`n")

$now = (Get-Date).ToString("s")
$tasks = @{}

function Add-Task($id, $lane, $idx, $bucket) {
  $outRel = "outputs\phase3\{0}.md" -f $id
  $objective = @()
  $objective += "PHASE3 REAL WORK. This is not a placeholder."
  $objective += "Create or update output file at: $outRel"
  $objective += "Write a concrete, useful content (min 20 lines) related to bucket: $bucket."
  $objective += "Include 1) what changed 2) why 3) acceptance check list."
  $objective += "If writer_mode=REAL, generate the content using LLM. If STUB, mark clearly [STUB_GEN]."
  $objectiveText = ($objective -join "`n")

  $accept = @()
  $accept += "output_file_exists: $outRel"
  $accept += "min_lines: 20"
  $accept += "must_include: acceptance check list"
  $accept += "must_not_be_only_placeholder: true"
  $acceptText = ($accept -join "`n")

  $tasks[$id] = @{
    id = $id
    lane = $lane
    priority = "P1"
    bucket = $bucket
    objective = $objectiveText
    outputs = @($outRel)
    acceptance = $acceptText
  }
}

$buckets = @("INTEGRATION_WELD", "EVIDENCE_PACK_HARDEN", "FAILBOX_REQUEUE", "DEVLOG_AUTORUN")

for ($i=0; $i -lt 120; $i++) {
  $lane = (($i % 8) + 1)
  $bucket = $buckets[$i % $buckets.Count]
  Add-Task $A[$i] $lane $i $bucket
}

for ($i=0; $i -lt 120; $i++) {
  $lane = (($i % 8) + 1)
  $bucket = $buckets[(($i + 2) % $buckets.Count)]
  Add-Task $B[$i] $lane ($i+120) $bucket
}

$catalog = @{
  schema_version = 2
  generated_at = $now
  root = $Root
  tasks = $tasks
}

$json = ($catalog | ConvertTo-Json -Depth 8)
Write-Utf8NoBom $catPath $json

Write-Host "[OK] Full Ammunition Loaded (240 Bullets)." -ForegroundColor Green