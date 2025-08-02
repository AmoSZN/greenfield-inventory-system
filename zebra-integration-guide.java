// ZebraIntegrationModule.java - Complete Zebra Integration for Greenfield Metal Sales
package com.paradigm.inventoryscanner.zebra;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.util.Log;
import com.zebra.sdk.comm.BluetoothConnection;
import com.zebra.sdk.comm.Connection;
import com.zebra.sdk.printer.PrinterLanguage;
import com.zebra.sdk.printer.ZebraPrinter;
import com.zebra.sdk.printer.ZebraPrinterFactory;
import java.util.ArrayList;
import java.util.List;

/**
 * Complete Zebra integration for scanners and printers
 * Replaces camera scanning with professional Zebra scanners
 * Enables direct printing to Zebra 610 printers
 */
public class ZebraIntegrationModule {
    private static final String TAG = "ZebraIntegration";
    
    // DataWedge Intent Actions
    private static final String DATAWEDGE_INTENT_ACTION = "com.paradigm.inventoryscanner.SCAN";
    private static final String DATAWEDGE_INTENT_KEY_DATA = "com.symbol.datawedge.data_string";
    private static final String DATAWEDGE_INTENT_KEY_SOURCE = "com.symbol.datawedge.source";
    
    private Context context;
    private ScanCallback scanCallback;
    private BroadcastReceiver scanReceiver;
    
    public interface ScanCallback {
        void onScan(String barcode, String symbology);
        void onBatchScan(List<String> barcodes);
    }
    
    public ZebraIntegrationModule(Context context) {
        this.context = context;
        setupDataWedge();
        setupScanReceiver();
    }
    
    /**
     * Configure DataWedge for optimal metal warehouse scanning
     */
    private void setupDataWedge() {
        sendDataWedgeIntentWithExtra(ACTION_DATAWEDGE, EXTRA_CREATE_PROFILE, "GreenfieldMetalProfile");
        
        // Configure scanner settings
        Bundle profileConfig = new Bundle();
        profileConfig.putString("PROFILE_NAME", "GreenfieldMetalProfile");
        profileConfig.putString("PROFILE_ENABLED", "true");
        profileConfig.putString("CONFIG_MODE", "UPDATE");
        
        // Scanner input plugin
        Bundle scannerConfig = new Bundle();
        scannerConfig.putString("PLUGIN_NAME", "BARCODE");
        scannerConfig.putString("RESET_CONFIG", "true");
        
        // Scanner parameters optimized for metal tags
        Bundle scannerProps = new Bundle();
        scannerProps.putString("scanner_selection", "auto");
        scannerProps.putString("scanner_input_enabled", "true");
        scannerProps.putString("decoder_code128", "true");
        scannerProps.putString("decoder_code39", "true");
        scannerProps.putString("decoder_datamatrix", "true");
        scannerProps.putString("decoder_qrcode", "true");
        
        // Aggressive decoding for damaged/dirty labels
        scannerProps.putString("decoder_code128_redundancy", "true");
        scannerProps.putString("decoder_code128_security_level", "1");
        scannerProps.putString("aim_mode", "on");
        scannerProps.putString("illumination_mode", "torch");
        scannerProps.putString("picklist_mode", "2"); // Hardware reticle
        scannerProps.putString("viewfinder_mode", "1"); // Dynamic reticle
        
        // Multi-barcode scanning for batch operations
        scannerProps.putString("scanning_mode", "multi_barcode");
        scannerProps.putString("multi_barcode_count", "10");
        
        scannerConfig.putBundle("PARAM_LIST", scannerProps);
        profileConfig.putBundle("PLUGIN_CONFIG", scannerConfig);
        
        // Intent output plugin
        Bundle intentConfig = new Bundle();
        intentConfig.putString("PLUGIN_NAME", "INTENT");
        intentConfig.putString("RESET_CONFIG", "true");
        
        Bundle intentProps = new Bundle();
        intentProps.putString("intent_output_enabled", "true");
        intentProps.putString("intent_action", DATAWEDGE_INTENT_ACTION);
        intentProps.putString("intent_delivery", "2"); // Broadcast
        intentConfig.putBundle("PARAM_LIST", intentProps);
        
        // Apply configurations
        ArrayList<Bundle> plugins = new ArrayList<>();
        plugins.add(scannerConfig);
        plugins.add(intentConfig);
        profileConfig.putParcelableArrayList("PLUGIN_CONFIG", plugins);
        
        sendDataWedgeIntentWithExtra(ACTION_SET_CONFIG, EXTRA_SET_CONFIG, profileConfig);
    }
    
    /**
     * Setup broadcast receiver for scan results
     */
    private void setupScanReceiver() {
        scanReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                String action = intent.getAction();
                if (DATAWEDGE_INTENT_ACTION.equals(action)) {
                    String barcode = intent.getStringExtra(DATAWEDGE_INTENT_KEY_DATA);
                    String source = intent.getStringExtra(DATAWEDGE_INTENT_KEY_SOURCE);
                    
                    if (barcode != null && !barcode.isEmpty()) {
                        Log.d(TAG, "Scanned: " + barcode + " from " + source);
                        
                        // Handle multi-barcode results
                        if (intent.hasExtra("com.symbol.datawedge.decode_data")) {
                            ArrayList<Bundle> scanData = intent.getParcelableArrayListExtra(
                                "com.symbol.datawedge.decode_data");
                            List<String> barcodes = new ArrayList<>();
                            
                            for (Bundle data : scanData) {
                                String code = data.getString("com.symbol.datawedge.decode_data");
                                if (code != null) barcodes.add(code);
                            }
                            
                            if (scanCallback != null && barcodes.size() > 1) {
                                scanCallback.onBatchScan(barcodes);
                            }
                        } else if (scanCallback != null) {
                            scanCallback.onScan(barcode, source);
                        }
                    }
                }
            }
        };
        
        IntentFilter filter = new IntentFilter();
        filter.addAction(DATAWEDGE_INTENT_ACTION);
        filter.addCategory(Intent.CATEGORY_DEFAULT);
        context.registerReceiver(scanReceiver, filter);
    }
    
    /**
     * Print label directly to Zebra 610 printer
     */
    public void printLabel(String productId, int quantity, PrintCallback callback) {
        new Thread(() -> {
            Connection printerConnection = null;
            try {
                // Find Zebra printer (USB, Network, or Bluetooth)
                printerConnection = findPrinter();
                printerConnection.open();
                
                ZebraPrinter printer = ZebraPrinterFactory.getInstance(
                    PrinterLanguage.ZPL, printerConnection);
                
                // Get product data from Paradigm
                InventoryItem item = paradigmAPI.getProduct(productId);
                
                // Generate ZPL for metal inventory label
                String zpl = generateMetalInventoryLabel(item, quantity);
                
                // Send to printer
                printerConnection.write(zpl.getBytes());
                
                callback.onPrintSuccess();
                
            } catch (Exception e) {
                Log.e(TAG, "Print error", e);
                callback.onPrintError(e.getMessage());
            } finally {
                if (printerConnection != null) {
                    try {
                        printerConnection.close();
                    } catch (Exception e) {}
                }
            }
        }).start();
    }
    
    /**
     * Generate ZPL code for Zebra 610 printer
     * Optimized 4x2 label for metal inventory
     */
    private String generateMetalInventoryLabel(InventoryItem item, int quantity) {
        StringBuilder zpl = new StringBuilder();
        
        // Start format
        zpl.append("^XA\n");
        
        // Set label home position
        zpl.append("^LH0,0\n");
        
        // Product ID Barcode (Code 128, high density)
        zpl.append("^FO50,30^BY2\n");
        zpl.append("^BCN,100,Y,N,N\n");
        zpl.append("^FD").append(item.getProductId()).append("^FS\n");
        
        // Product ID Text
        zpl.append("^FO50,140^A0N,40,40\n");
        zpl.append("^FD").append(item.getProductId()).append("^FS\n");
        
        // Description (wrapped)
        zpl.append("^FO50,190^A0N,25,25^FB700,2,0,L,0\n");
        zpl.append("^FD").append(item.getDescription()).append("^FS\n");
        
        // Location barcode (smaller, in corner)
        if (item.getLocation() != null) {
            zpl.append("^FO500,30^BY1\n");
            zpl.append("^BCN,50,N,N,N\n");
            zpl.append("^FD").append(item.getLocation()).append("^FS\n");
            
            zpl.append("^FO500,85^A0N,20,20\n");
            zpl.append("^FDLoc: ").append(item.getLocation()).append("^FS\n");
        }
        
        // Quantity and other details
        zpl.append("^FO50,250^A0N,30,30\n");
        zpl.append("^FDQty: ").append(quantity).append(" ").append(item.getUOM()).append("^FS\n");
        
        zpl.append("^FO350,250^A0N,30,30\n");
        zpl.append("^FDPrice: $").append(String.format("%.2f", item.getPrice())).append("^FS\n");
        
        // Category and date
        zpl.append("^FO50,290^A0N,20,20\n");
        zpl.append("^FDCat: ").append(item.getCategory()).append("^FS\n");
        
        zpl.append("^FO350,290^A0N,20,20\n");
        zpl.append("^FD").append(getCurrentDate()).append("^FS\n");
        
        // QR code with full data (for mobile scanning)
        String qrData = String.format("ID:%s|QTY:%d|LOC:%s|PRICE:%.2f",
            item.getProductId(), quantity, item.getLocation(), item.getPrice());
        
        zpl.append("^FO550,150^BQN,2,4\n");
        zpl.append("^FDQA,").append(qrData).append("^FS\n");
        
        // End format
        zpl.append("^XZ");
        
        return zpl.toString();
    }
    
    /**
     * Cycle count mode - rapid scanning with audio feedback
     */
    public void startCycleCount(List<String> expectedItems) {
        // Configure for rapid scanning
        Bundle rapidConfig = new Bundle();
        rapidConfig.putString("PROFILE_NAME", "GreenfieldMetalProfile");
        rapidConfig.putString("CONFIG_MODE", "UPDATE");
        
        Bundle scannerConfig = new Bundle();
        scannerConfig.putString("aim_type", "4"); // Continuous read
        scannerConfig.putString("same_barcode_timeout", "500"); // Allow quick re-scans
        scannerConfig.putString("different_barcode_timeout", "200");
        scannerConfig.putString("decode_audio_feedback_mode", "3"); // Unique tone per symbology
        
        sendDataWedgeIntentWithExtra(ACTION_SET_CONFIG, EXTRA_SET_CONFIG, rapidConfig);
        
        // Track scanned items
        this.scanCallback = new ScanCallback() {
            private List<String> scannedItems = new ArrayList<>();
            
            @Override
            public void onScan(String barcode, String symbology) {
                if (expectedItems.contains(barcode)) {
                    if (!scannedItems.contains(barcode)) {
                        scannedItems.add(barcode);
                        // Green LED flash for expected item
                        flashLED(GREEN);
                        playSound(SOUND_SUCCESS);
                    } else {
                        // Already counted
                        flashLED(YELLOW);
                        playSound(SOUND_DUPLICATE);
                    }
                } else {
                    // Unexpected item
                    flashLED(RED);
                    playSound(SOUND_ERROR);
                }
                
                // Update UI
                updateCycleCountProgress(scannedItems.size(), expectedItems.size());
            }
        };
    }
    
    /**
     * Helper methods
     */
    private void sendDataWedgeIntentWithExtra(String action, String extraKey, Bundle extras) {
        Intent dwIntent = new Intent();
        dwIntent.setAction(action);
        dwIntent.putExtra(extraKey, extras);
        context.sendBroadcast(dwIntent);
    }
    
    private Connection findPrinter() {
        // Try USB first (for Zebra 610 desktop printer)
        try {
            return new UsbConnection(context);
        } catch (Exception e) {
            // Try network
            String printerIP = getConfiguredPrinterIP();
            if (printerIP != null) {
                return new TcpConnection(printerIP, 9100);
            }
            // Fallback to Bluetooth
            return new BluetoothConnection(getConfiguredPrinterMAC());
        }
    }
    
    public void cleanup() {
        if (scanReceiver != null) {
            context.unregisterReceiver(scanReceiver);
        }
    }
}

// MetalWarehouseActivity.java - Optimized UI for metal warehouse operations
public class MetalWarehouseActivity extends AppCompatActivity {
    private ZebraIntegrationModule zebraModule;
    private TextView tvLastScan;
    private TextView tvLocationDisplay;
    private RecyclerView rvBatchScans;
    private Button btnPrintLabel;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_metal_warehouse);
        
        // Initialize Zebra integration
        zebraModule = new ZebraIntegrationModule(this);
        
        // Set scan callback
        zebraModule.setScanCallback(new ZebraIntegrationModule.ScanCallback() {
            @Override
            public void onScan(String barcode, String symbology) {
                // Vibrate for feedback
                vibrate(50);
                
                // Parse barcode
                if (barcode.contains("|")) {
                    // Location barcode format: LOC|A-12-3-B
                    handleLocationScan(barcode);
                } else {
                    // Product barcode
                    handleProductScan(barcode);
                }
            }
            
            @Override
            public void onBatchScan(List<String> barcodes) {
                // Multiple items scanned at once
                processBatchReceiving(barcodes);
            }
        });
    }
    
    private void handleProductScan(String productId) {
        // Quick lookup and action menu
        paradigmAPI.getProduct(productId, product -> {
            runOnUiThread(() -> {
                showQuickActionMenu(product);
            });
        });
    }
    
    private void showQuickActionMenu(InventoryItem product) {
        BottomSheetDialog dialog = new BottomSheetDialog(this);
        View sheet = getLayoutInflater().inflate(R.layout.quick_action_sheet, null);
        
        // Display product info
        TextView tvProduct = sheet.findViewById(R.id.tvProductInfo);
        tvProduct.setText(String.format("%s\n%s\nStock: %d | Location: %s",
            product.getProductId(),
            product.getDescription(),
            product.getQuantity(),
            product.getLocation()
        ));
        
        // Quick actions
        sheet.findViewById(R.id.btnQuickAdd).setOnClickListener(v -> {
            quickAdjustInventory(product.getProductId(), 1);
            dialog.dismiss();
        });
        
        sheet.findViewById(R.id.btnQuickRemove).setOnClickListener(v -> {
            quickAdjustInventory(product.getProductId(), -1);
            dialog.dismiss();
        });
        
        sheet.findViewById(R.id.btnMoveLocation).setOnClickListener(v -> {
            startLocationMove(product.getProductId());
            dialog.dismiss();
        });
        
        sheet.findViewById(R.id.btnPrintLabel).setOnClickListener(v -> {
            zebraModule.printLabel(product.getProductId(), 1, new PrintCallback() {
                @Override
                public void onPrintSuccess() {
                    showToast("Label printed!");
                }
            });
            dialog.dismiss();
        });
        
        dialog.setContentView(sheet);
        dialog.show();
    }
}