## Handling Nested JSON Structures

This guide explains how to convert complex nested JSON structures to Excel format using the JSON to Excel Conversion Tool. Nested JSON structures contain objects within objects, creating a hierarchical data structure that requires special handling during conversion to tabular format.

## Prerequisites

Before you begin, ensure you have:

- Installed the JSON to Excel Conversion Tool (see [Installation Guide](../installation.md))
- Understanding of basic JSON to Excel conversion principles
- Understanding of JSON structure and terminology (objects, arrays, nesting)

## Basic Single File Conversion

Before diving into complex nested structures, it's helpful to understand the basic single file conversion process. To convert a single JSON file to Excel format, use the command:

```bash
json2excel convert input.json output.xlsx
```

This converts the JSON file to Excel format with default settings. For flat JSON structures (simple key-value pairs), the conversion creates one row per object with columns for each key.

## Understanding Nested JSON

Nested JSON structures contain objects or arrays within other objects, creating a hierarchical data structure. For example:

```json
{
  "id": 1,
  "name": "John Doe",
  "contact": {
    "email": "john.doe@example.com",
    "phone": "555-1234",
    "address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip": "12345"
    }
  },
  "profile": {
    "age": 30,
    "active": true
  }
}
```

In this example, `contact` and `profile` are nested objects, and `address` is nested within `contact`. This creates multiple levels of nesting that must be flattened when converting to Excel's tabular format.

## How the Tool Handles Nested JSON

The JSON to Excel Conversion Tool handles nested structures by flattening them using dot notation for column names. For example, the nested path `contact.address.city` becomes a column named `contact.address.city` in the Excel output.

This approach preserves the hierarchical relationship between data elements while converting to a tabular format suitable for Excel.

## Example 1: Converting a Nested JSON File

Let's convert a nested JSON file to Excel format.

1. Create a file named `customer.json` with the following content:

```json
{
  "id": 1,
  "name": "John Doe",
  "contact": {
    "email": "john.doe@example.com",
    "phone": "555-1234",
    "address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip": "12345"
    }
  },
  "profile": {
    "age": 30,
    "active": true
  }
}
```

2. Run the conversion command:

```bash
json2excel convert customer.json customer.xlsx
```

3. Open the resulting `customer.xlsx` file in Excel. You should see a spreadsheet with one row of data and columns including:
   - id
   - name
   - contact.email
   - contact.phone
   - contact.address.street
   - contact.address.city
   - contact.address.state
   - contact.address.zip
   - profile.age
   - profile.active

## Example 2: Customizing the Path Separator

By default, the tool uses a dot (`.`) as the separator for nested paths. You can customize this using the `--separator` option:

```bash
json2excel convert customer.json customer.xlsx --separator="_"
```

This will create an Excel file with column names like:
- id
- name
- contact_email
- contact_phone
- contact_address_street
- contact_address_city
- contact_address_state
- contact_address_zip
- profile_age
- profile_active

Choosing a different separator can be useful when your data already contains dots in field names or when you prefer a different naming convention.

## Example 3: Limiting Nesting Depth

For very deeply nested JSON structures, you might want to limit the nesting depth to make the output more manageable. Use the `--max-depth` option to specify the maximum nesting level to process:

```bash
json2excel convert deeply_nested.json output.xlsx --max-depth=3
```

This will process nested structures only up to 3 levels deep. Any deeper nesting will be truncated or represented as JSON strings, depending on the structure.

## Handling Arrays in Nested Structures

Nested JSON structures often contain arrays, which add another dimension of complexity. The tool provides two strategies for handling arrays:

1. **Expand** (default): Creates multiple rows, one for each array element
2. **Join**: Combines array elements into a single cell with a separator

Let's look at examples of both approaches.

## Example 4: Arrays of Primitive Values

Consider a JSON file with arrays of primitive values:

```json
{
  "id": 1,
  "name": "John Doe",
  "tags": ["customer", "premium", "active"],
  "contact": {
    "email": "john.doe@example.com",
    "phone_numbers": ["555-1234", "555-5678"]
  }
}
```

**Using the default expand mode:**

```bash
json2excel convert customer_with_arrays.json output.xlsx
```

This will create an Excel file with multiple rows, expanding the arrays:

| id | name     | tags     | contact.email          | contact.phone_numbers |
|----|----------|----------|------------------------|----------------------|
| 1  | John Doe | customer | john.doe@example.com   | 555-1234             |
| 1  | John Doe | premium  | john.doe@example.com   | 555-5678             |
| 1  | John Doe | active   | john.doe@example.com   | null                 |

**Using join mode:**

```bash
json2excel convert customer_with_arrays.json output.xlsx --array-handling=join
```

This will create an Excel file with a single row, joining the arrays:

| id | name     | tags                       | contact.email          | contact.phone_numbers      |
|----|----------|----------------------------|------------------------|---------------------------|
| 1  | John Doe | customer, premium, active  | john.doe@example.com   | 555-1234, 555-5678        |

## Example 5: Arrays of Objects

Arrays of objects are more complex and are always expanded into multiple rows. Consider this JSON file:

```json
{
  "id": 1,
  "name": "John Doe",
  "orders": [
    {
      "id": 101,
      "product": "Laptop",
      "price": 999.99,
      "shipping": {
        "method": "Express",
        "cost": 15.99
      }
    },
    {
      "id": 102,
      "product": "Mouse",
      "price": 24.99,
      "shipping": {
        "method": "Standard",
        "cost": 5.99
      }
    }
  ]
}
```

Running the conversion:

```bash
json2excel convert customer_with_order_array.json output.xlsx
```

This will create an Excel file with multiple rows, expanding the orders array:

| id | name     | orders.id | orders.product | orders.price | orders.shipping.method | orders.shipping.cost |
|----|----------|-----------|----------------|--------------|------------------------|----------------------|
| 1  | John Doe | 101       | Laptop         | 999.99       | Express                | 15.99                |
| 1  | John Doe | 102       | Mouse          | 24.99        | Standard               | 5.99                 |

Note that the nested structure within each array item (shipping) is also flattened using dot notation.

## Example 6: Selecting Specific Fields

For complex nested structures, you might want to extract only specific fields. Use the `--fields` option to specify which fields to include in the output:

```bash
json2excel convert customer.json output.xlsx --fields="id,name,contact.email,contact.address.city,profile.age"
```

This will create an Excel file with only the specified fields as columns:

| id | name     | contact.email          | contact.address.city | profile.age |
|----|----------|------------------------|----------------------|-------------|
| 1  | John Doe | john.doe@example.com   | Anytown              | 30          |

This is particularly useful for large, complex JSON structures where you only need certain fields.

## Example 7: Deeply Nested Structures

Let's look at a more complex example with deep nesting:

```json
{
  "id": 1,
  "name": "John Doe",
  "account": {
    "type": "premium",
    "details": {
      "payment_methods": {
        "primary": {
          "type": "credit_card",
          "last_four": "1234",
          "expiry": "12/25"
        },
        "secondary": {
          "type": "bank_account",
          "account_number": "****5678"
        }
      },
      "preferences": {
        "notifications": {
          "email": true,
          "sms": false,
          "push": {
            "enabled": true,
            "frequency": "daily"
          }
        }
      }
    }
  }
}
```

Running the conversion:

```bash
json2excel convert deeply_nested.json output.xlsx
```

This will create an Excel file with columns using dot notation for the deeply nested paths:

| id | name     | account.type | account.details.payment_methods.primary.type | account.details.payment_methods.primary.last_four | ... |
|----|----------|--------------|---------------------------------------------|--------------------------------------------------|-----|
| 1  | John Doe | premium      | credit_card                                 | 1234                                             | ... |

For very deep nesting (beyond 5-6 levels), column names can become quite long. In such cases, consider using a shorter separator with `--separator` or selecting specific fields with `--fields`.

## Best Practices for Handling Nested JSON

When working with nested JSON structures, consider these best practices:

1. **Analyze the structure first**: Use `json2excel info your_file.json` to understand the structure before conversion

2. **Use verbose mode**: Add `--verbose` to see detailed information about the conversion process

3. **For very complex structures**:
   - Select only needed fields with `--fields`
   - Limit nesting depth with `--max-depth`
   - Use a shorter separator with `--separator`

4. **For large files with nested arrays**:
   - Consider using `--chunk-size` to process in smaller batches
   - Use `--array-handling=join` if appropriate for your data

5. **For better Excel readability**:
   - Use `--auto-column-width` to adjust column widths
   - Use `--format-as-table` for easier filtering and sorting
   - Use `--freeze-header` to keep column headers visible

## Troubleshooting Nested JSON Conversion

Here are solutions to common issues when converting nested JSON:

1. **Excel column names are too long**:
   - Use a shorter separator: `--separator="_"`
   - Select specific fields: `--fields="id,name,contact.email"`

2. **Memory errors with large nested structures**:
   - Use chunked processing: `--chunk-size=1000`
   - Limit nesting depth: `--max-depth=3`

3. **Too many rows from array expansion**:
   - Use join mode for arrays: `--array-handling=join`
   - Filter the data before conversion

4. **Unexpected null values in output**:
   - Check if the nested path exists consistently across all objects
   - Arrays of different lengths can cause misalignment

5. **Excel row limit exceeded**:
   - Filter the data to reduce rows
   - Split the output into multiple files

## Next Steps

Now that you've learned how to handle nested JSON structures, you might want to explore:

- [Batch Processing](./batch_processing.md): Learn how to convert multiple JSON files in a single operation
- [API Reference](../api_reference.md): Comprehensive documentation of all available options and parameters

For more information about all available options and features, run:

```bash
json2excel help convert
```