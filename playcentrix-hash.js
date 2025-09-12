async function playcentrixHash(input) {
  const SALT = "Playcentrix-Hash";

  async function sha(algorithm, message) {
    const data = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest(algorithm, data);
    return [...new Uint8Array(hashBuffer)]
      .map(b => b.toString(16).padStart(2, "0"))
      .join("");
  }

  let hash = await sha("SHA-256", input + SALT);
  for (let i = 0; i < 15; i++) {
    hash = await sha("SHA-512", hash + SALT);
  }
  return hash;
}