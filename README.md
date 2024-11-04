# Memory Management API

This project is a FastAPI application for managing and retrieving memory data. It includes endpoints for creating and retrieving memories, with support for user-specific data and flexible query options.

## Features

- **Create Memory**: Store memory data with user association.
- **Retrieve Memories**: Fetch memories with options for date range, transcript inclusion, and user filtering.

## Endpoints

### POST /memory-created

- **Description**: Create a new memory record.
- **Query Parameters**:
  - `uid`: User ID associated with the memory.
- **Request Body**: JSON object with memory details.
- **Response**: JSON object with status and memory ID.

### GET /memories/

- **Description**: Retrieve memories for a specific user.
- **Query Parameters**:
  - `user_id`: User ID to filter memories.
  - `start_date`: Start date for filtering memories (optional).
  - `end_date`: End date for filtering memories (optional).
  - `include_transcripts`: Whether to include full transcripts (optional).
- **Response**: JSON array of memory objects.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd omiapi
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   uvicorn main:app --reload
   ```

4. **Run Tests**:
   ```bash
   pytest test_main.py
   ```

## Development

- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **API Framework**: FastAPI

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. 