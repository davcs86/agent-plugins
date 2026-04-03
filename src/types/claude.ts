export type Role = 'user' | 'assistant'

export interface Message {
  role: Role
  content: string
}
