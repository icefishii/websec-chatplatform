# WebSec Chat Platform - API Testing Script (Windows PowerShell)
# This script demonstrates all available API endpoints

$ErrorActionPreference = "Stop"

# API Base URL
$ApiUrl = "https://localhost:8443/api/v1"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  WebSec Chat Platform API Demo" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Register Users
Write-Host "[1/11] Registering users..." -ForegroundColor Yellow
Write-Host "POST /register" -ForegroundColor Green

$aliceResp = Invoke-WebRequest -Uri "$ApiUrl/register" -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"alice","profile_name":"Alice Wonderland","password":"SecurePass123!"}' `
  -SkipCertificateCheck
$alice = $aliceResp.Content | ConvertFrom-Json
Write-Host "Alice registered:" -ForegroundColor Green
$alice | Format-List
$aliceId = $alice.id

$bobResp = Invoke-WebRequest -Uri "$ApiUrl/register" -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"bob","profile_name":"Bob Builder","password":"SecurePass123!"}' `
  -SkipCertificateCheck
$bob = $bobResp.Content | ConvertFrom-Json
Write-Host "Bob registered:" -ForegroundColor Green
$bob | Format-List
$bobId = $bob.id

$charlieResp = Invoke-WebRequest -Uri "$ApiUrl/register" -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"charlie","profile_name":"Charlie Chaplin","password":"SecurePass123!"}' `
  -SkipCertificateCheck
$charlie = $charlieResp.Content | ConvertFrom-Json
Write-Host "Charlie registered:" -ForegroundColor Green
$charlie | Format-List
$charlieId = $charlie.id

Read-Host "`nPress Enter to continue"

# Test 2: Login as Alice
Write-Host "`n[2/11] Logging in as Alice..." -ForegroundColor Yellow
Write-Host "POST /login" -ForegroundColor Green

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$loginResp = Invoke-WebRequest -Uri "$ApiUrl/login" -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"alice","password":"SecurePass123!"}' `
  -WebSession $session `
  -SkipCertificateCheck
$loginResp.Content | ConvertFrom-Json | Format-List

Read-Host "`nPress Enter to continue"

# Test 3: Get Current User
Write-Host "`n[3/11] Getting current user info..." -ForegroundColor Yellow
Write-Host "GET /me" -ForegroundColor Green

$meResp = Invoke-WebRequest -Uri "$ApiUrl/me" `
  -WebSession $session `
  -SkipCertificateCheck
$meResp.Content | ConvertFrom-Json | Format-List

Read-Host "`nPress Enter to continue"

# Test 4: Search Users
Write-Host "`n[4/11] Searching for users..." -ForegroundColor Yellow
Write-Host "GET /users/search?q=alice" -ForegroundColor Green

$searchResp = Invoke-WebRequest -Uri "$ApiUrl/users/search?q=alice" `
  -WebSession $session `
  -SkipCertificateCheck
$searchResp.Content | ConvertFrom-Json | Format-Table

Write-Host "GET /users/search?q=bob&limit=5" -ForegroundColor Green
$searchResp2 = Invoke-WebRequest -Uri "$ApiUrl/users/search?q=bob&limit=5" `
  -WebSession $session `
  -SkipCertificateCheck
$searchResp2.Content | ConvertFrom-Json | Format-Table

Read-Host "`nPress Enter to continue"

# Test 5: Send Messages
Write-Host "`n[5/11] Sending messages from Alice to Bob..." -ForegroundColor Yellow
Write-Host "POST /messages" -ForegroundColor Green

$msg1Resp = Invoke-WebRequest -Uri "$ApiUrl/messages" -Method POST `
  -ContentType "application/json" `
  -Body "{`"recipient_id`":`"$bobId`",`"content`":`"Hey Bob, how are you doing?`"}" `
  -WebSession $session `
  -SkipCertificateCheck
Write-Host "Message 1 sent:" -ForegroundColor Green
$msg1Resp.Content | ConvertFrom-Json | Format-List

$msg2Resp = Invoke-WebRequest -Uri "$ApiUrl/messages" -Method POST `
  -ContentType "application/json" `
  -Body "{`"recipient_id`":`"$bobId`",`"content`":`"Looking forward to chatting with you!`"}" `
  -WebSession $session `
  -SkipCertificateCheck
Write-Host "Message 2 sent:" -ForegroundColor Green
$msg2Resp.Content | ConvertFrom-Json | Format-List

$msg3Resp = Invoke-WebRequest -Uri "$ApiUrl/messages" -Method POST `
  -ContentType "application/json" `
  -Body "{`"recipient_id`":`"$charlieId`",`"content`":`"Hi Charlie! Welcome to the platform.`"}" `
  -WebSession $session `
  -SkipCertificateCheck
Write-Host "Message 3 sent to Charlie:" -ForegroundColor Green
$msg3Resp.Content | ConvertFrom-Json | Format-List

Read-Host "`nPress Enter to continue"

# Test 6: Login as Bob and Reply
Write-Host "`n[6/11] Logging in as Bob and replying..." -ForegroundColor Yellow
Write-Host "POST /login (as Bob)" -ForegroundColor Green

$bobSession = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$bobLoginResp = Invoke-WebRequest -Uri "$ApiUrl/login" -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"bob","password":"SecurePass123!"}' `
  -WebSession $bobSession `
  -SkipCertificateCheck
$bobLoginResp.Content | ConvertFrom-Json | Format-List

Write-Host "POST /messages (Bob -> Alice)" -ForegroundColor Green
$bobMsg1Resp = Invoke-WebRequest -Uri "$ApiUrl/messages" -Method POST `
  -ContentType "application/json" `
  -Body "{`"recipient_id`":`"$aliceId`",`"content`":`"Hi Alice! I'm doing great, thanks for asking!`"}" `
  -WebSession $bobSession `
  -SkipCertificateCheck
$bobMsg1Resp.Content | ConvertFrom-Json | Format-List

$bobMsg2Resp = Invoke-WebRequest -Uri "$ApiUrl/messages" -Method POST `
  -ContentType "application/json" `
  -Body "{`"recipient_id`":`"$aliceId`",`"content`":`"How about you?`"}" `
  -WebSession $bobSession `
  -SkipCertificateCheck
$bobMsg2Resp.Content | ConvertFrom-Json | Format-List

Read-Host "`nPress Enter to continue"

# Test 7: Get Conversations List
Write-Host "`n[7/11] Getting Bob's conversations list..." -ForegroundColor Yellow
Write-Host "GET /messages/conversations" -ForegroundColor Green

$bobConvResp = Invoke-WebRequest -Uri "$ApiUrl/messages/conversations" `
  -WebSession $bobSession `
  -SkipCertificateCheck
$bobConvResp.Content | ConvertFrom-Json | Format-Table

Read-Host "`nPress Enter to continue"

# Test 8: Get Conversation Messages
Write-Host "`n[8/11] Getting full conversation between Bob and Alice..." -ForegroundColor Yellow
Write-Host "GET /messages/$aliceId" -ForegroundColor Green

$bobMsgsResp = Invoke-WebRequest -Uri "$ApiUrl/messages/$aliceId" `
  -WebSession $bobSession `
  -SkipCertificateCheck

Write-Host "`nConversation between Bob and Alice:" -ForegroundColor Cyan
$msgs = $bobMsgsResp.Content | ConvertFrom-Json
foreach ($msg in $msgs) {
    $sender = if ($msg.sender_id -eq $aliceId) { "Alice" } else { "Bob" }
    $color = if ($sender -eq "Alice") { "Cyan" } else { "Green" }
    Write-Host "[$($msg.created_at)] $sender`: $($msg.content)" -ForegroundColor $color
}

Read-Host "`nPress Enter to continue"

# Test 9: Login back as Alice
Write-Host "`n[9/11] Logging back in as Alice..." -ForegroundColor Yellow
Write-Host "POST /login (as Alice)" -ForegroundColor Green

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$aliceLoginResp = Invoke-WebRequest -Uri "$ApiUrl/login" -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"alice","password":"SecurePass123!"}' `
  -WebSession $session `
  -SkipCertificateCheck
$aliceLoginResp.Content | ConvertFrom-Json | Format-List

# Test 10: Get Alice's Conversations
Write-Host "`n[10/11] Getting Alice's conversations list..." -ForegroundColor Yellow
Write-Host "GET /messages/conversations" -ForegroundColor Green

$aliceConvResp = Invoke-WebRequest -Uri "$ApiUrl/messages/conversations" `
  -WebSession $session `
  -SkipCertificateCheck
$aliceConvResp.Content | ConvertFrom-Json | Format-Table

Read-Host "`nPress Enter to continue"

# Test 11: Logout
Write-Host "`n[11/11] Logging out..." -ForegroundColor Yellow
Write-Host "POST /logout" -ForegroundColor Green

$logoutResp = Invoke-WebRequest -Uri "$ApiUrl/logout" -Method POST `
  -WebSession $session `
  -SkipCertificateCheck
$logoutResp.Content | ConvertFrom-Json | Format-List

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  All API endpoints tested! ✓" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Summary of tested endpoints:" -ForegroundColor Yellow
Write-Host "  ✓ POST   /register" -ForegroundColor Green
Write-Host "  ✓ POST   /login" -ForegroundColor Green
Write-Host "  ✓ GET    /me" -ForegroundColor Green
Write-Host "  ✓ GET    /users/search" -ForegroundColor Green
Write-Host "  ✓ POST   /messages" -ForegroundColor Green
Write-Host "  ✓ GET    /messages/conversations" -ForegroundColor Green
Write-Host "  ✓ GET    /messages/{user_id}" -ForegroundColor Green
Write-Host "  ✓ POST   /logout" -ForegroundColor Green

Write-Host "`nUser IDs created:" -ForegroundColor Cyan
Write-Host "  Alice:   $aliceId" -ForegroundColor White
Write-Host "  Bob:     $bobId" -ForegroundColor White
Write-Host "  Charlie: $charlieId" -ForegroundColor White

Write-Host "`nTip: View interactive docs at https://localhost:8443/api/v1/docs" -ForegroundColor Yellow
Write-Host ""
