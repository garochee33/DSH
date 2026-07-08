import 'server-only'
import os from 'node:os'
import path from 'node:path'
import { exec as execCb } from 'node:child_process'
import { promisify } from 'node:util'

const exec = promisify(execCb)

const HOME = os.homedir()
const DSH_ROOT = path.join(HOME, 'DSH')

export type RepoStatus = {
  name: string
  path: string
  branch: string | null
  uncommitted: number
  staged: number
  untracked: number
  ahead: number
  behind: number
  lastCommit: { sha: string; subject: string; author: string; iso: string } | null
  stompRisk: 'none' | 'low' | 'high'
  stompReason: string | null
  error: string | null
}

const REPOS: Array<{ name: string; path: string }> = [
  { name: 'DSH', path: DSH_ROOT },
  { name: 'DSH', path: path.join(DSH_ROOT, 'home', 'DSH') },
  { name: 'trinity-unified-ai', path: path.join(DSH_ROOT, 'home', 'trinity-unified-ai') },
  { name: 'dsh-console', path: path.join(DSH_ROOT, 'home', 'projects', 'dsh-console') },
]

async function git(repo: string, args: string): Promise<string> {
  const { stdout } = await exec(`git -C ${JSON.stringify(repo)} ${args}`, { timeout: 4000, maxBuffer: 1024 * 1024 })
  return stdout
}

async function getOne(repo: { name: string; path: string }): Promise<RepoStatus> {
  const base: RepoStatus = {
    name: repo.name,
    path: repo.path,
    branch: null,
    uncommitted: 0,
    staged: 0,
    untracked: 0,
    ahead: 0,
    behind: 0,
    lastCommit: null,
    stompRisk: 'none',
    stompReason: null,
    error: null,
  }
  try {
    const branch = (await git(repo.path, 'rev-parse --abbrev-ref HEAD')).trim()
    base.branch = branch || null

    const status = await git(repo.path, 'status --porcelain=v1 --untracked-files=all')
    const lines = status.split('\n').filter(Boolean)
    for (const line of lines) {
      const code = line.slice(0, 2)
      if (code.startsWith('?')) base.untracked += 1
      else {
        if (code[0] !== ' ' && code[0] !== '?') base.staged += 1
        if (code[1] !== ' ' && code[1] !== '?') base.uncommitted += 1
      }
    }

    try {
      const ahead = await git(repo.path, `rev-list --count @{u}..HEAD`)
      const behind = await git(repo.path, `rev-list --count HEAD..@{u}`)
      base.ahead = Number(ahead.trim()) || 0
      base.behind = Number(behind.trim()) || 0
    } catch {
      // no upstream — leave defaults
    }

    try {
      const fmt = '%H%x09%s%x09%an%x09%aI'
      const out = (await git(repo.path, `log -1 --format=${JSON.stringify(fmt)}`)).trim()
      const [sha, subject, author, iso] = out.split('\t')
      if (sha) base.lastCommit = { sha, subject: subject ?? '', author: author ?? '', iso: iso ?? '' }
    } catch {
      // no commits
    }

    if (base.behind > 0 && (base.uncommitted > 0 || base.staged > 0)) {
      base.stompRisk = 'high'
      base.stompReason = `${base.behind} commit${base.behind === 1 ? '' : 's'} behind upstream with local changes — rebase/merge will conflict`
    } else if (base.behind > 0) {
      base.stompRisk = 'low'
      base.stompReason = `${base.behind} commit${base.behind === 1 ? '' : 's'} behind upstream — pull before working`
    } else if (base.ahead > 0 && base.uncommitted + base.staged + base.untracked > 0) {
      base.stompRisk = 'low'
      base.stompReason = `${base.ahead} commit${base.ahead === 1 ? '' : 's'} unpushed with active local edits — another agent may amend`
    }
  } catch (err) {
    base.error = err instanceof Error ? err.message : String(err)
  }
  return base
}

export async function getRepos(): Promise<RepoStatus[]> {
  return Promise.all(REPOS.map(getOne))
}
