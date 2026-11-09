import { PublicNav } from '../components/AppNav';
import { CONTACT_EMAIL, LEGAL_UPDATED, OPERATOR } from '../legal';
import { Link } from '../router';

export function TermsPage() {
  return (
    <div className="pl-page">
      <PublicNav />
      <main id="main" tabIndex={-1} className="pl-wrap pl-wrap--narrow pl-app-main pl-stack pl-gap-5 pl-privacy">
        <div>
          <h1 className="pl-display-md">Terms of Service</h1>
          <p className="pl-small pl-muted">Updated {LEGAL_UPDATED}</p>
          <p className="pl-lead">
            These terms apply when you use MathLoop. By creating an account or using the service, you agree to them.
          </p>
        </div>

        <section aria-labelledby="terms-who">
          <h2 id="terms-who" className="pl-h-lg">Who provides MathLoop</h2>
          <p>
            MathLoop is a free beta run by {OPERATOR}, an individual developer, not a company. “We” on this page means the operator.
            Contact: <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.
          </p>
        </section>

        <section aria-labelledby="terms-service">
          <h2 id="terms-service" className="pl-h-lg">The service</h2>
          <p>
            MathLoop generates mathematics problems, checks your answers, shows solutions and keeps a history of your
            practice. It is free, and there are no payments or subscriptions. Because it is a beta, features can change,
            be limited or stop at any time.
          </p>
        </section>

        <section aria-labelledby="terms-account">
          <h2 id="terms-account" className="pl-h-lg">Your account</h2>
          <p>
            Accounts are for learners aged 16 and over and use Google sign-in. You are responsible for what happens under
            your account, so keep your Google account secure. You can delete your MathLoop account at any time on your{' '}
            <Link to="/profile">profile</Link>.
          </p>
        </section>

        <section aria-labelledby="terms-use">
          <h2 id="terms-use" className="pl-h-lg">Acceptable use</h2>
          <p>Please use MathLoop for study and do not:</p>
          <ul className="pl-stack pl-gap-2">
            <li>attack, overload or try to get around the security or rate limits of the service;</li>
            <li>access other people’s accounts or data;</li>
            <li>collect problems or solutions in bulk with automated tools, or resell or republish them as your own service;</li>
            <li>submit unlawful, abusive or harmful content in problem reports or your display name.</li>
          </ul>
        </section>

        <section aria-labelledby="terms-accuracy">
          <h2 id="terms-accuracy" className="pl-h-lg">Problems and solutions can contain mistakes</h2>
          <p>
            We test the generators, but a problem, answer check, solution or graph can still be wrong. MathLoop is a
            practice tool, so do not rely on it alone for an exam, grade or other important decision. If something looks
            wrong, use “Report a problem” on the problem page.
          </p>
        </section>

        <section aria-labelledby="terms-content">
          <h2 id="terms-content" className="pl-h-lg">Your content and shared problems</h2>
          <p>
            What you write, such as answers and problem reports, stays yours. You allow us to store and use it to run the
            service and fix faulty problems. A share link or code lets anyone who has it see the problem statement, topic
            and difficulty, but not your answers, results or solutions. Links end after 90 days and you can stop them earlier.
          </p>
        </section>

        <section aria-labelledby="terms-ip">
          <h2 id="terms-ip" className="pl-h-lg">Our work</h2>
          <p>
            The MathLoop software, design and generators belong to their authors. You may use generated problems,
            solutions and worksheets for your own study and teaching. Other use needs our permission.
          </p>
        </section>

        <section aria-labelledby="terms-liability">
          <h2 id="terms-liability" className="pl-h-lg">No guarantee, and limits of liability</h2>
          <p>
            MathLoop is provided as it is, without a promise that it will always be available, free of errors or keep
            your data forever. The database currently has no automatic backups, so your history could be lost. To the
            extent the law allows, we are not liable for indirect loss, lost data or results that depend on the service.
            Nothing here limits liability that cannot be limited by law or removes your mandatory consumer rights.
          </p>
        </section>

        <section aria-labelledby="terms-ending">
          <h2 id="terms-ending" className="pl-h-lg">Ending your use</h2>
          <p>
            You can stop using MathLoop whenever you like. We may suspend or close an account that breaks these terms
            or puts the service at risk, and we may shut the service down. Where reasonably possible, we will give notice first.
          </p>
        </section>

        <section aria-labelledby="terms-changes">
          <h2 id="terms-changes" className="pl-h-lg">Changes and questions</h2>
          <p>
            If these terms change, we will update this page and its date. How we handle your data is explained in the{' '}
            <Link to="/privacy">Privacy</Link> page. Questions are welcome at{' '}
            <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.
          </p>
        </section>
      </main>
    </div>
  );
}
