Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text = "Greenfield Metal Sales - Order Label Printing"
$form.Size = New-Object System.Drawing.Size(700,500)
$form.StartPosition = "CenterScreen"

# Order Number Input
$lblOrder = New-Object System.Windows.Forms.Label
$lblOrder.Text = "Enter Order Number:"
$lblOrder.Location = New-Object System.Drawing.Point(20,20)
$lblOrder.Size = New-Object System.Drawing.Size(150,20)

$txtOrder = New-Object System.Windows.Forms.TextBox
$txtOrder.Location = New-Object System.Drawing.Point(20,50)
$txtOrder.Size = New-Object System.Drawing.Size(200,25)
$txtOrder.Text = "0005915"  # Sample order from your API

# Buttons
$btnLookup = New-Object System.Windows.Forms.Button
$btnLookup.Text = "Lookup Order"
$btnLookup.Location = New-Object System.Drawing.Point(240,50)
$btnLookup.Size = New-Object System.Drawing.Size(100,25)

$btnPrint = New-Object System.Windows.Forms.Button
$btnPrint.Text = "Print Label"
$btnPrint.Location = New-Object System.Drawing.Point(360,50)
$btnPrint.Size = New-Object System.Drawing.Size(100,25)
$btnPrint.Enabled = $false

$btnListOrders = New-Object System.Windows.Forms.Button
$btnListOrders.Text = "List All Orders"
$btnListOrders.Location = New-Object System.Drawing.Point(480,50)
$btnListOrders.Size = New-Object System.Drawing.Size(100,25)

# Results area
$txtResults = New-Object System.Windows.Forms.TextBox
$txtResults.Location = New-Object System.Drawing.Point(20,90)
$txtResults.Size = New-Object System.Drawing.Size(640,350)
$txtResults.Multiline = $true
$txtResults.ScrollBars = "Vertical"
$txtResults.ReadOnly = $true
$txtResults.Font = New-Object System.Drawing.Font("Consolas", 9)

# Event handlers
$btnLookup.Add_Click({
    $orderNumber = $txtOrder.Text.Trim()
    if ([string]::IsNullOrEmpty($orderNumber)) {
        [System.Windows.Forms.MessageBox]::Show("Please enter an order number", "Error")
        return
    }
    
    try {
        $txtResults.Text = "Looking up order $orderNumber..."
        $txtResults.Refresh()
        
        $response = Invoke-RestMethod -Uri "http://localhost:5003/api/order/$orderNumber" -Method Get
        
        if ($response.status -eq "success") {
            $order = $response.order
            $results = @"
✅ ORDER FOUND: $($order.orderNumber)

📋 ORDER DETAILS:
Customer PO: $($order.customerPO)
Order Date: $($order.orderDate)
Total Amount: $($order.totalAmount)

👤 CUSTOMER INFO:
Name: $($order.customerName)

📦 BILL TO:
$($order.billToCompany)
$($order.billToAddress)
$($order.billToCity), $($order.billToState) $($order.billToZIP)

🚚 SHIP TO:
$($order.shipToCompany)
$($order.shipToAddress)
$($order.shipToCity), $($order.shipToState) $($order.shipToZIP)

📦 PRODUCTS:
"@
            
            foreach ($product in $order.products) {
                $results += "`n- ID: $($product.productId)"
                $results += "`n  Description: $($product.description)"
                $results += "`n  Quantity: $($product.quantity)"
                $results += "`n  Unit Price: $($product.unitPrice)"
                $results += "`n  Extended: $($product.extendedPrice)"
                $results += "`n"
            }
            
            $results += "`n📁 FILES:"
            $results += "`nCSV File: $($response.csv_file)"
            
            $txtResults.Text = $results
            $btnPrint.Enabled = $true
        } else {
            $txtResults.Text = "❌ ERROR: $($response.message)"
            $btnPrint.Enabled = $false
        }
    } catch {
        $txtResults.Text = "❌ ERROR: Could not connect to service.`n`nMake sure the integration service is running!`n`nError: $($_.Exception.Message)"
        $btnPrint.Enabled = $false
    }
})

$btnPrint.Add_Click({
    $orderNumber = $txtOrder.Text.Trim()
    try {
        $txtResults.AppendText("`n`n🖨️ PRINTING LABEL...")
        $txtResults.Refresh()
        
        $printData = @{order_number = $orderNumber} | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "http://localhost:5003/api/print-label" -Method Post -Body $printData -ContentType "application/json"
        
        if ($response.status -eq "success") {
            $txtResults.AppendText("`n✅ Label printed successfully!")
            [System.Windows.Forms.MessageBox]::Show("Label sent to printer!", "Success", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
        } else {
            $txtResults.AppendText("`n❌ Print failed: $($response.message)")
        }
    } catch {
        $txtResults.AppendText("`n❌ Print error: $($_.Exception.Message)")
        [System.Windows.Forms.MessageBox]::Show("Error printing: $($_.Exception.Message)", "Error")
    }
})

$btnListOrders.Add_Click({
    try {
        $txtResults.Text = "Loading all orders..."
        $txtResults.Refresh()
        
        $response = Invoke-RestMethod -Uri "http://localhost:5003/api/orders" -Method Get
        
        if ($response.status -eq "success") {
            $results = "📋 ALL ORDERS:`n`n"
            foreach ($order in $response.orders) {
                $results += "Order: $($order.orderNumber) | Customer: $($order.customerName) | Date: $($order.orderDate) | Total: $($order.total)`n"
            }
            $txtResults.Text = $results
        } else {
            $txtResults.Text = "❌ ERROR: $($response.message)"
        }
    } catch {
        $txtResults.Text = "❌ ERROR: $($_.Exception.Message)"
    }
})

# Add controls to form
$form.Controls.AddRange(@($lblOrder, $txtOrder, $btnLookup, $btnPrint, $btnListOrders, $txtResults))

# Show form
$form.ShowDialog()
