from django.urls import path
from inventory.views import Index, SignUpView, Dashboard, TransactionsView, \
    CreateInboundTransactionView, CreateOutboundTransactionView, CreateTransferTransactionView, \
    DrugMasterView, CreateDrugMasterView, EditDrugMasterView, InventoryCalendarView, CategoryView, \
    SiteView, CreateCategoryView, CreateSiteView, EditCategoryView, EditSiteView, filtered_drugs, \
    get_filtered_lots, UserView, EditUserView, CreateAdjustTransactionView, \
    ExportTransCSV, databar_parser, CancelTransactionView, InventoryValidationView, \
    populate_safety_stock, ExportDrugMasterView, \
    ImportDrugMasterView, SafetyStockMatrixView, populate_kana, ConfirmTransferView, \
    PendingConfirmationsView, CustomPasswordChangeView, InventoryInspectionView, \
    InventoryInspectionHistoryView, InventoryBatchAdjustmentView, CustomLogoutView, ExportInventoryInspectionView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", Index.as_view(), name='index'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('transactions/', TransactionsView.as_view(), name='transactions'),
    path('export-transactions/', ExportTransCSV.as_view(), name='export-transactions'),
    path('transactions/create/inbound/', CreateInboundTransactionView.as_view(),
         name='create_inbound_transaction'),
    path('transactions/create/outbound/', CreateOutboundTransactionView.as_view(),
         name='create_outbound_transaction'),
    path('transactions/create/transfer/', CreateTransferTransactionView.as_view(),
         name='create_transfer_transaction'),
    path('transactions/create/adjust/', CreateAdjustTransactionView.as_view(),
         name='create_adjust_transaction'),
    path('transactions/cancel/<int:pk>/', CancelTransactionView.as_view(),
         name='cancel_transaction'),
    path('transactions/confirm/<int:pk>/', ConfirmTransferView.as_view(),
         name='confirm_transfer'),
    path('confirmations/', PendingConfirmationsView.as_view(), name='pending_confirmations'),
    path("drugs/", DrugMasterView.as_view(), name='drugs'),
    path('create-drug-master/', CreateDrugMasterView.as_view(), name='create-drug-master'),
    path('edit-drug-master/<int:pk>', EditDrugMasterView.as_view(), name='edit-drug-master'),
    path('calendar-view/', InventoryCalendarView.as_view(), name='calendar-view'),
    path('categories/', CategoryView.as_view(), name='categories'),
    path('create-category/', CreateCategoryView.as_view(), name='create-category'),
    path('edit-category/<int:pk>', EditCategoryView.as_view(), name='edit-category'),
    path('sites/', SiteView.as_view(), name='sites'),
    path('create-site/', CreateSiteView.as_view(), name='create-site'),
    path('edit-site/<int:pk>', EditSiteView.as_view(), name='edit-site'),
    path('users/', UserView.as_view(), name='users'),
    path('edit-user/<int:pk>', EditUserView.as_view(), name='edit-user'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('validation/', InventoryValidationView.as_view(), name="validation"),
    path('inventory-inspection/', InventoryInspectionView.as_view(), name="inspection"),
    path('inspection-history/', InventoryInspectionHistoryView.as_view(), name='inspection-history'),
    path('batch-adjustment/', InventoryBatchAdjustmentView.as_view(), name='batch-adjustment'),
    path("signup/", SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='inventory/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(template_name='inventory/logout.html'), name='logout'),
    path('populate-safety-stock/', populate_safety_stock, name='populate-safety-stock'),
    path('populate-kana/', populate_kana, name='populate-kana'),
    path('safety-stock-matrix/', SafetyStockMatrixView.as_view(), name='safety-stock-matrix'),
    path('export/drug-master/', ExportDrugMasterView.as_view(), name='drug-master-export'),
    path('import/drug-master/', ImportDrugMasterView.as_view(), name='drug-master-import'),
    path('inventory/export-inspection/', ExportInventoryInspectionView.as_view(), name='export_inventory_csv'),
    path('ajax/filtered-drugs/', filtered_drugs, name='filtered-drugs'),
    path('ajax/get_filtered_lots/', get_filtered_lots, name='get_filtered_lots'),
    path('ajax/databar_parser/', databar_parser, name='databar_parser'),
]
