import { ApiProperty } from '@nestjs/swagger';
import { IsEmail, IsString, MinLength, IsOptional } from 'class-validator';

export class RegisterDto {
    @ApiProperty({
        description: 'User email address',
        example: 'user@example.com',
    })
    @IsEmail()
    email: string;

    @ApiProperty({
        description: 'User password',
        example: 'password123',
        minLength: 8,
    })
    @IsString()
    @MinLength(8)
    password: string;

    @ApiProperty({
        description: 'User first name',
        example: 'John',
        required: false,
    })
    @IsOptional()
    @IsString()
    firstName?: string;

    @ApiProperty({
        description: 'User last name',
        example: 'Doe',
        required: false,
    })
    @IsOptional()
    @IsString()
    lastName?: string;

    @ApiProperty({
        description: 'Organization name',
        example: 'My Company',
        required: false,
    })
    @IsOptional()
    @IsString()
    organizationName?: string;
}
