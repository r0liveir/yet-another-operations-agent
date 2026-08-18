-- vector extension
create extension if not exists vector;


-- table to hold chunked documents and embeddings
create table if not exists document_chunks (
	id serial primary key,
	doc_id text not null,
	doc_title text not null,
	doc_type text not null,
	service text not null,
	source text not null,
	content text not null,
	embedding vector(768), -- must match dimensions of the embedding model
	created_at timestamptz default now()
);

-- indexing that makes similarity searches fast
create index if not exists doc_chunks_service_idx
on document_chunks (service, doc_type);
create index if not exists doc_chunks_embedding_hnsw
on document_chunks using hnsw (embedding vector_cosine_ops);
