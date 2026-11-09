import { PublicNav } from '../components/AppNav';
import { Button } from '../components/Button';
import { cookiebotEnabled, openCookieSettings } from '../cookieConsent';
import { CONTACT_EMAIL, LEGAL_UPDATED, OPERATOR } from '../legal';
import { Link } from '../router';

// Describes the data flows in this repository and nothing else. Update it with
// any change to what is stored, who processes it, analytics or backups.

const LEGAL_BASES = [
  'To provide your account, practice, history, statistics and share links: performing our agreement with you (GDPR Article 6(1)(b)).',
  'To keep the service secure, stop abuse, keep technical logs and fix faulty problems: our legitimate interest in running a safe and working service (Article 6(1)(f)).',
  'To meet a legal duty, if one applies (Article 6(1)(c)).',
];

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
    role: 'Serves this website and forwards API requests.',
    where: 'Cloudflare’s global network.',
  },
  {
    name: 'Oracle Cloud',
    role: 'Runs the MathLoop API, which generates problems and checks answers.',
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

const COOKIEBOT = {
  name: 'Cookiebot (Usercentrics)',
  role: 'Shows the cookie banner, records your consent choice and receives your browser’s technical data when it loads.',
  where: 'Usercentrics’ own terms apply.',
};

export function PrivacyPage() {
  const consentBanner = cookiebotEnabled();
  const processors = consentBanner ? [...PROCESSORS, COOKIEBOT] : PROCESSORS;
  return (
    <div className="pl-page">
      <PublicNav />
      <main id="main" tabIndex={-1} className="pl-wrap pl-wrap--narrow pl-app-main pl-stack pl-gap-5 pl-privacy">
        <div>
          <div className="pl-label">Updated {LEGAL_UPDATED}</div>
          <h1 className="pl-display-md pl-mt-4">Privacy</h1>
          <p className="pl-lead">
            This page describes what MathLoop does with your data today, who is responsible for it and what your
            rights are.
          </p>
        </div>

        <section aria-labelledby="privacy-who">
          <h2 id="privacy-who" className="pl-h-lg">Who runs MathLoop</h2>
          <p>
            MathLoop is a free beta run by {OPERATOR}, an individual developer, who is the controller of your data under
            the GDPR. “We” on this page means the operator. For any privacy question or request, write to{' '}
            <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.
          </p>
        </section>

        <section aria-labelledby="privacy-without">
          <h2 id="privacy-without" className="pl-h-lg">Without an account</h2>
          <p>
            You can browse the curriculum, solve one demo problem and open a shared problem without signing in. A demo
            answer is sent to the API to be checked and is not stored, and we do not create a profile of you. Like most web
            servers, the API writes a short technical log line for each request (address, path and status).
            We keep these logs only as long as we need them to run and secure the service.
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

        <section aria-labelledby="privacy-bases">
          <h2 id="privacy-bases" className="pl-h-lg">Why we may use your data</h2>
          <ul className="pl-stack pl-gap-2">
            {LEGAL_BASES.map((item) => <li key={item}>{item}</li>)}
          </ul>
          <p>You cannot have an account without the sign-in data above, because it is how the account works.</p>
        </section>

        <section aria-labelledby="privacy-browser">
          <h2 id="privacy-browser" className="pl-h-lg">In your browser</h2>
          <p>
            {consentBanner
              ? 'MathLoop itself sets no cookies. Our Cookiebot consent banner stores your choice in a cookie, so it does not ask again on every visit.'
              : 'MathLoop sets no cookies.'}{' '}
            When you sign in, your session is kept in your browser’s local storage so you stay signed in; logging out
            removes it. Fonts are served from this website, not from a third party.
          </p>
          {consentBanner && <Button variant="secondary" size="sm" onClick={() => openCookieSettings()}>Change cookie settings</Button>}
        </section>

        <section aria-labelledby="privacy-analytics">
          <h2 id="privacy-analytics" className="pl-h-lg">Analytics</h2>
          <p>
            MathLoop currently uses no analytics or advertising tools. Your learning statistics are calculated from
            your own data in our database and are shown only to you.
          </p>
        </section>

        <section aria-labelledby="privacy-processors">
          <h2 id="privacy-processors" className="pl-h-lg">Who processes it</h2>
          <dl className="pl-stack pl-gap-3">
            {processors.map((item) => (
              <div key={item.name}>
                <dt className="pl-h-md">{item.name}</dt>
                <dd className="pl-m-0">{item.role} {item.where}</dd>
              </div>
            ))}
          </dl>
          <p>
            Some of these providers operate worldwide, so some data may be processed outside the European Economic Area.
            Where that happens, we rely on the safeguards the providers offer for such transfers, such as the EU standard
            contractual clauses.
          </p>
        </section>

        <section aria-labelledby="privacy-delete">
          <h2 id="privacy-delete" className="pl-h-lg">Keeping and deleting your data</h2>
          <p>
            Your data is kept while you have an account. You can delete your account yourself on your{' '}
            <Link to="/profile">profile</Link>. Deletion removes your account, problems, attempts, shares and reports
            immediately. The database currently has no automatic backups; any recovery copy made by hand must be
            deleted within 30 days.
          </p>
        </section>

        <section aria-labelledby="privacy-rights">
          <h2 id="privacy-rights" className="pl-h-lg">Your rights</h2>
          <p>
            You can see, correct and delete your data in the app. Under EU data-protection law (GDPR) you can also ask us
            for access to your data or a copy of it, to correct, delete or restrict it, and object to uses based on our
            legitimate interest. Write to <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.
          </p>
          <p>
            You can also complain to a data-protection authority, for example where you live. In Ireland that is the Data
            Protection Commission, and in Poland the President of the Personal Data Protection Office (UODO).
          </p>
        </section>

        <section aria-labelledby="privacy-changes">
          <h2 id="privacy-changes" className="pl-h-lg">Changes</h2>
          <p>
            If this page changes, we will update it and its date. The rules for using MathLoop are in the{' '}
            <Link to="/terms">Terms of Service</Link>.
          </p>
        </section>
      </main>
    </div>
  );
}
