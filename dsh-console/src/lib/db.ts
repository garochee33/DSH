// Stub — public build has no SQLite database
export function getDb(): any {
  return {
    prepare: () => ({ get: () => ({ n: 0 }), all: () => [] }),
  }
}
