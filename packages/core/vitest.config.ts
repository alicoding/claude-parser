/**
 * @fileoverview Vitest configuration
 * 
 * ENGINEERING PATTERN: Type-safe test configuration
 * - Explicit test patterns
 * - Coverage requirements enforced
 * - TypeScript-first testing
 */

import { defineConfig } from 'vitest/config'
import { resolve } from 'path'

export default defineConfig({
  test: {
    // Test file patterns
    include: [
      'src/**/__tests__/**/*.test.ts',
      'src/**/*.test.ts',
      'tests/**/*.test.ts'
    ],
    exclude: [
      'node_modules',
      'dist',
      '.turbo'
    ],
    
    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules',
        'dist',
        '**/*.test.ts',
        '**/__tests__/**',
        '**/index.ts' // Barrel exports don't need coverage
      ],
      thresholds: {
        branches: 95,
        functions: 95,
        lines: 95,
        statements: 95
      }
    },
    
    // Test environment
    environment: 'node',
    
    // TypeScript support
    globals: true,
    
    // Reporter configuration
    reporters: ['verbose'],
    
    // Test timeout
    testTimeout: 10000,
    
    // Watch mode exclusions
    watchExclude: ['**/node_modules/**', '**/dist/**']
  },
  
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@models': resolve(__dirname, './src/models'),
      '@parser': resolve(__dirname, './src/parser'),
      '@utils': resolve(__dirname, './src/utils')
    }
  }
})