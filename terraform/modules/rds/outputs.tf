output "database_endpoint" {
  description = "The connection endpoint for the RDS instance"
  value       = aws_db_instance.main.endpoint
}

output "database_name" {
  description = "The name of the database"
  value       = aws_db_instance.main.db_name
}

output "database_username" {
  description = "The master username for the database"
  value       = aws_db_instance.main.username
}

output "database_port" {
  description = "The database port"
  value       = aws_db_instance.main.port
}
