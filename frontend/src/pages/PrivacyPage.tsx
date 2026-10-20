import { Logo, PublicNav } from '../components/AppNav';
import { Link } from '../router';

// Draft (#38): it describes the data flows in this repository and nothing else.
// The operator's legal identity, contact address, legal bases and the final
// backup window are launch blockers (#39) and are stated as open, never guessed.

const PROCESSORS = [
  {
    name: 'Supabase',
    role: 'Google sign-in and the database that holds your account and practice data.',
    where: 'Database in the EU (Ireland, eu-west-1).',
  },
  {
    name: 'Google',
    role: 'Sign-in only. Google tells us your email address, name and account ID after you agree on its page.',
    where: 'Google’s own terms apply to your Google account.',
  },
  {
    name: 'Cloudflare',
    role: 'Serves this website, forwards API requests and, if enabled, counts anonymous page views and page speed (Cloudflare Web Analytics).',
    where: 'Cloudflare’s global network.',
  },
  {
    name: 'Oracle Cloud',
    role: 'Runs the PracticeLoop API, which generates problems and checks answers.',
    where: 'EU (Frankfurt).',
  },
];

const STORED = [
  'Your Google account email address, name, profile picture link and Google account ID, kept by Supabase Auth to sign you in.',
  'An optional display name, which you can change or remove on your profile.',
  'Each problem you generate: its topic, difficulty, statement, generator version, answer and solution.',
  'Each answer you submit, whether it was correct, the kind of mistake we detected, how long you took, and whether you revealed the answer or the solution.',
  'Links and codes you create to share a problem. They show only the statement, topic and difficulty, end after 90 days and can be stopped earlier.',
  'Problem reports you send: the problem, a category and an optional comment.',
  'Short-lived request keys that stop a double click from saving something twice, deleted after 24 hours.',
];

export function PrivacyPage() {
  return (
    <div className="pl-page">
      <PublicNav />
      <main id="main" tabIndex={-1} className="pl-wrap pl-wrap--narrow pl-app-main pl-stack pl-gap-5 pl-privacy">
        <div>
          <div className="pl-label">Draft</div>
          <h1 className="pl-display-md pl-mt-4">Privacy</h1>
          <p className="pl-lead">
            This draft describes what PracticeLoop actually does with your data today. It is not final: the items under
            “Not decided yet” must be completed before public launch.
          </p>
        </div>

        <section aria-labelledby="privacy-who">
          <h2 id="privacy-who" className="pl-h-lg">Who runs PracticeLoop</h2>
          <p>
            PracticeLoop is a free beta built in Poland. The operator’s full legal name, address and a privacy contact
            email will be published here before launch. They are not listed yet.
          </p>
        </section>

        <section aria-labelledby="privacy-without">
          <h2 id="privacy-without" className="pl-h-lg">Without an account</h2>
          <p>
            You can solve one demo problem without signing in. Your answer is sent to the API to be checked and is not
            stored. Like most web servers, the API writes a short technical log line for each request (address, path and
            status), never your answer.
          </p>
        </section>

        <section aria-labelledby="privacy-stored">
          <h2 id="privacy-stored" className="pl-h-lg">What we store when you sign in</h2>
          <p>Accounts are for learners aged 16 and over. We store:</p>
          <ul className="pl-stack pl-gap-2">
            {STORED.map((item) => <li key={item}>{item}</li>)}
          </ul>
          <p>
            We use this to run the practice, show your history and statistics, and fix faulty problems. Nobody else can
            see it: every database query is limited to your own account. There are no adverts, payments or newsletters.
          </p>
        </section>

        <section aria-labelledby="privacy-browser">
          <h2 id="privacy-browser" className="pl-h-lg">In your browser</h2>
          <p>
            PracticeLoop sets no cookies. When you sign in, your session is kept in your browser’s local storage so you
            stay signed in; logging out removes it. Fonts are served from this website, not from a third party.
          </p>
        </section>

        <section aria-labelledby="privacy-analytics">
          <h2 id="privacy-analytics" className="pl-h-lg">Analytics</h2>
          <p>
            If enabled, Cloudflare Web Analytics counts page views and measures page speed without cookies or local
            storage. It never receives your email address, account ID or answers, and it is not loaded on sign-in or
            shared-problem pages. Your learning statistics are calculated from your own data in our database.
          </p>
        </section>

        <section aria-labelledby="privacy-processors">
          <h2 id="privacy-processors" className="pl-h-lg">Who processes it</h2>
          <dl className="pl-stack pl-gap-3">
            {PROCESSORS.map((item) => (
              <div key={item.name}>
                <dt className="pl-h-md">{item.name}</dt>
                <dd className="pl-m-0">{item.role} {item.where}</dd>
              </div>
            ))}
          </dl>
        </section>

        <section aria-labelledby="privacy-delete">
          <h2 id="privacy-delete" className="pl-h-lg">Keeping and deleting your data</h2>
          <p>
            Your data is kept while you have an account. You can delete your account yourself on your{' '}
            <Link to="/profile">profile</Link>. Deletion removes your account, problems, attempts, shares and reports
            immediately. The database currently has no automatic backups; any recovery copy made by hand must be
            deleted within 30 days. The backup setup for launch will be confirmed here.
          </p>
        </section>

        <section aria-labelledby="privacy-rights">
          <h2 id="privacy-rights" className="pl-h-lg">Your rights</h2>
          <p>
            You can see, correct and delete your data in the app. Under EU data-protection law (GDPR) you can also ask
            for a copy of your data, object to its use, and complain to a data-protection authority; in Poland that is
            the President of the Personal Data Protection Office (UODO).
          </p>
        </section>

        <section aria-labelledby="privacy-open" className="pl-card pl-stack pl-gap-3">
          <h2 id="privacy-open" className="pl-h-lg">Not decided yet</h2>
          <ul className="pl-stack pl-gap-2 pl-m-0">
            <li>The operator’s legal identity and address.</li>
            <li>A dedicated privacy contact email.</li>
            <li>The legal basis for each use of data, after legal review.</li>
            <li>The backup setup and its retention period.</li>
            <li>Whether Cloudflare Web Analytics is switched on.</li>
          </ul>
        </section>
      </main>
      <footer className="pl-wrap pl-row pl-small pl-subtle pl-footer">
        <Logo />
        <Link to="/">Home</Link>
      </footer>
    </div>
  );
}
