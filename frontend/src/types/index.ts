export interface User {
  id: number
  name: string
  email: string
  role: UserRole
  created_at: string
  updated_at?: string
}

export interface Invoice {
  id: number
  user_id: number
  date: string
  provider: string
  amount: number
  payment_method: PaymentMethod
  category: ExpenseCategory
  file_path?: string
  description?: string
  status: InvoiceStatus
  created_at: string
  updated_at?: string
  user: User
  nit?: string
  gmail_attachments?: GmailAttachment[]
}

export interface GmailAttachment {
  filename: string
  mime_type: string
  size: number
  attachment_id: string
  download_url: string
}

export interface CreateUserRequest {
  name: string
  email: string
  role: UserRole
}

export interface CreateInvoiceRequest {
  date: string
  provider: string
  amount: number
  payment_method: PaymentMethod
  category: ExpenseCategory
  user_id: number
  description?: string
  nit?: string
}

export interface UpdateUserRequest {
  name?: string
  email?: string
  role?: UserRole
}

export interface UpdateInvoiceRequest {
  date?: string
  provider?: string
  amount?: number
  payment_method?: PaymentMethod
  category?: ExpenseCategory
  description?: string
  status?: InvoiceStatus
  nit?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface InvoiceFilters {
  user_id?: number
  status?: InvoiceStatus
  category?: ExpenseCategory
  payment_method?: PaymentMethod
  start_date?: string
  end_date?: string
  provider?: string
  page?: number
  size?: number
}

export interface ExportResponse {
  message: string
  file_path: string
  total_invoices: number
}

export enum UserRole {
  COLLABORATOR = 'colaborador',
  ACCOUNTING_ASSISTANT = 'auxiliar_contable',
  FINANCIAL_MANAGER = 'gerencia_financiera',
  ADMIN = 'administrador'
}

export enum PaymentMethod {
  CASH = 'CASH',
  CARD = 'CARD',
  CARD_PERSONAL = 'CHECK',  // Tarjeta Personal (usando CHECK que no se usa)
  TRANSFER = 'TRANSFER'
}

export enum ExpenseCategory {
  TRANSPORT = 'transporte',
  MEALS = 'alimentacion',
  ACCOMMODATION = 'hospedaje',
  SUPPLIES = 'suministros',
  COMMUNICATION = 'comunicacion',
  OTHER = 'otros'
}

export enum InvoiceStatus {
  PENDING = 'pendiente',
  VALIDATED = 'validada',
  REJECTED = 'rechazada'
}

export const USER_ROLE_LABELS: Record<UserRole, string> = {
  [UserRole.COLLABORATOR]: 'Colaborador',
  [UserRole.ACCOUNTING_ASSISTANT]: 'Auxiliar Contable',
  [UserRole.FINANCIAL_MANAGER]: 'Gerencia Financiera',
  [UserRole.ADMIN]: 'Administrador'
}

export const PAYMENT_METHOD_LABELS: Record<PaymentMethod, string> = {
  [PaymentMethod.CASH]: 'Efectivo',
  [PaymentMethod.CARD]: 'Tarjeta BST',
  [PaymentMethod.CARD_PERSONAL]: 'Tarjeta Personal',
  [PaymentMethod.TRANSFER]: 'Transferencia'
}

export const EXPENSE_CATEGORY_LABELS: Record<ExpenseCategory, string> = {
  [ExpenseCategory.TRANSPORT]: 'Transporte',
  [ExpenseCategory.MEALS]: 'Alimentación',
  [ExpenseCategory.ACCOMMODATION]: 'Hospedaje',
  [ExpenseCategory.SUPPLIES]: 'Suministros',
  [ExpenseCategory.COMMUNICATION]: 'Comunicación',
  [ExpenseCategory.OTHER]: 'Otros'
}

export const INVOICE_STATUS_LABELS: Record<InvoiceStatus, string> = {
  [InvoiceStatus.PENDING]: 'Pendiente',
  [InvoiceStatus.VALIDATED]: 'Validada',
  [InvoiceStatus.REJECTED]: 'Rechazada'
}

export const INVOICE_STATUS_COLORS: Record<InvoiceStatus, string> = {
  [InvoiceStatus.PENDING]: 'bg-warning-100 text-warning-800',
  [InvoiceStatus.VALIDATED]: 'bg-success-100 text-success-800',
  [InvoiceStatus.REJECTED]: 'bg-error-100 text-error-800'
}

// Tipos para análisis de facturas desde Gmail
export interface InvoiceAnalysisResult {
  email_id: string
  email_subject: string
  email_from: string
  provider: string
  amount: number
  date: string
  description?: string
  attachments: Array<{
    filename: string
    mime_type: string
    size: number
  }>
  suggested_user_id?: number
  suggested_user_name?: string
  reason_no_user?: string
}

export interface InvoiceAnalysisSummary {
  total_emails_analyzed: number
  invoices_found: number
  invoices_with_user: number
  invoices_without_user: number
  already_uploaded: number
}

export interface InvoiceAnalysisResponse {
  success: boolean
  summary: InvoiceAnalysisSummary
  invoices_to_upload: InvoiceAnalysisResult[]
  invoices_without_user: InvoiceAnalysisResult[]
  already_uploaded: Array<{
    email_id: string
    email_subject: string
    provider: string
    amount: number
    date: string
    existing_invoice_id: number
    existing_user: string
  }>
  query_used: string
  analysis_date: string
}

export interface BulkInvoiceItem {
  email_id: string
  email_subject: string
  email_from: string
  provider: string
  amount: number
  date: string
  description?: string
  user_id?: number  // Hacer opcional para facturas sin usuario
  payment_method: PaymentMethod
  category: ExpenseCategory
  nit?: string
}

export interface BulkInvoiceCreate {
  invoices: BulkInvoiceItem[]
  skip_duplicates: boolean
}

export interface BulkInvoiceResponse {
  success: boolean
  total_processed: number
  created_count: number
  skipped_count: number
  error_count: number
  created_invoices: number[]
  skipped_invoices: string[]
  errors: Array<{
    email_id: string
    error: string
  }>
}
