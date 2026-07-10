import os
import django
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from applicant.models import AgreementTemplate, AgreementTemplateClause
from country.models import Country
from core.choices import AgreementType, ClauseVisibilityMode

class Command(BaseCommand):
    help = "Seeds the database with Agreement Template 1 and Template 2"

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing Applicant references to old agreements...")
        from applicant.models import Applicant
        Applicant.objects.filter(agreement__isnull=False).update(agreement=None)

        self.stdout.write("Deleting existing AgreementTemplates...")
        AgreementTemplate.objects.all().delete()
        AgreementTemplateClause.objects.all().delete()

        # Try to find Saudi Arabia in the DB, or create a dummy one for seeding
        saudi_country = Country.objects.filter(name__icontains="Saudi").first()
        if not saudi_country:
            self.stdout.write(self.style.WARNING("Saudi Arabia country not found in DB. Creating a placeholder."))
            saudi_country = Country.objects.create(
                name="Saudi Arabia",
                code="SA",
                slug="saudi-arabia",
                currency="SAR",
                language="Arabic",
            )

        # -------------------------------------------------------------------
        # TEMPLATE 1
        # -------------------------------------------------------------------
        self.stdout.write("Creating Agreement Template 1 (Main Agreement)...")
        template_1 = AgreementTemplate.objects.create(
            title="Employment & Visa Service Agreement",
            code="main-agreement-v1",
            agreement_type=AgreementType.MAIN,
            version=1,
            is_active=True,
            is_default=True,
        )

        template_1_clauses = [
            {
                "num": 1,
                "title_en": "ACKNOWLEDGEMENT OF RECEIPT",
                "title_ar": "إقرار الاستلام",
                "title_bn": "অর্থ গ্রহণের স্বীকৃতি",
                "body_en": "I am {staff_name}, as the authorized representative of Al-Raiyan Group, Saudi Arabia, hereby certify that I have received the above mentioned amount and that the said amount shall be subject to the terms and conditions stated in this receipt and agreement.",
                "body_ar": "أنا، {staff_name}، بصفتي الممثل المعتمد لمجموعة الريان، المملكة العربية السعودية، أشهد بموجب هذا أنني قد استلمت المبلغ المذكور أعلاه وأن هذا المبلغ يخضع للشروط والأحكام الواردة في هذا الإيصال والاتفاقية.",
                "body_bn": "আমি {staff_name}, আল-রাইয়ান গ্রুপ, সৌদি আরব-এর অনুমোদিত প্রতিনিধি হিসেবে এই মর্মে প্রত্যয়ন করিতেছি যে, উপরে উল্লিখিত অর্থ আমি গ্রহণ করিয়াছি এবং উক্ত অর্থ এই রিসিট ও চুক্তিপত্রে বর্ণিত শর্তাবলীর আওতাভুক্ত থাকিবে।"
            },
            {
                "num": 2,
                "title_en": "IMPORTANT NOTICE",
                "title_ar": "إشعار هام",
                "title_bn": "গুরুত্বপূর্ণ ঘোষণা",
                "body_en": "I am {staff_name}, hereby acknowledge receipt of the above-mentioned amount on behalf of Al-Raiyan Group, Kingdom of Saudi Arabia. I shall remain responsible for the collected funds until such funds are deposited into the official company account. However, I have no authority or liability regarding visa approval or employment guarantees.",
                "body_ar": "أنا، {staff_name}، أقر باستلام المبلغ المذكور أعلاه نيابةً عن مجموعة الريان – المملكة العربية السعودية. وأتحمل المسؤولية عن الأموال المستلمة حتى إيداعها في الحساب الرسمي للشركة. ولا أتحمل أي مسؤولية أو صلاحية فيما يتعلق بالموافقة على التأشيرة أو ضمان الوظيفة.",
                "body_bn": "আমি {staff_name}, আল-রাইয়ান গ্রুপ, সৌদি আরব-এর পক্ষে উল্লিখিত অর্থ গ্রহণ করিলাম। কোম্পানির অফিসিয়াল হিসাব নম্বরে জমা প্রদান না হওয়া পর্যন্ত উক্ত অর্থের দায়িত্ব আমার উপর বর্তাইবে। তবে ভিসা অনুমোদন বা চাকরির নিশ্চয়তা প্রদানের বিষয়ে আমার কোনো ক্ষমতা বা দায়বদ্ধতা নাই।"
            },
            {
                "num": 3,
                "title_en": "RESPONSIBILITY",
                "title_ar": "المسؤولية",
                "title_bn": "দায়িত্ব",
                "body_en": "Mr. {staff_name}'s responsibility is strictly limited to the collection of payments and the facilitation of the 80% refund in accordance with the terms of this Agreement. All responsibilities relating to visa processing, employment contracts, recruitment, and job placement shall remain the sole responsibility of Al-Raiyan Group, Kingdom of Saudi Arabia.",
                "body_ar": "تقتصر مسؤولية السيد {staff_name} على استلام المبالغ المالية وضمان استرداد نسبة 80٪ وفقاً لأحكام هذه الاتفاقية. أما جميع المسؤوليات المتعلقة بالتأشيرة والتوظيف وعقود العمل فتقع حصرياً على عاتق مجموعة الريان – المملكة العربية السعودية.",
                "body_bn": "জনাব {staff_name} এর দায়িত্ব কেবল অর্থ গ্রহণ এবং এই চুক্তির শর্ত অনুযায়ী ৮০% অর্থ ফেরত প্রদানের সমন্বয়ের মধ্যে সীমাবদ্ধ। ভিসা প্রসেসিং, চাকরির চুক্তিপত্র, বিদেশে নিয়োগ এবং কর্মসংস্থান সংক্রান্ত সকল দায়িত্ব একমাত্র আল-রাইয়ান গ্রুপ, সৌদি আরব বহন করিবে।"
            },
            {
                "num": 4,
                "title_en": "Visa & Employment Responsibility",
                "title_ar": "مسؤولية التأشيرة والتوظيف",
                "title_bn": "ভিসা ও চাকরির দায়িত্ব",
                "body_en": "Al-Raiyan Group shall bear full responsibility for visa processing, recruitment, employment facilitation, and all related services in accordance with the applicable laws and regulations of the Kingdom of Saudi Arabia.",
                "body_ar": "تتحمل مجموعة الريان المسؤولية الكاملة عن إجراءات التأشيرة والتوظيف والخدمات ذات الصلة وفقاً للأنظمة المعمول بها في المملكة العربية السعودية.",
                "body_bn": "ভিসা প্রসেসিং, নিয়োগ কার্যক্রম, চাকরি প্রদান এবং সংশ্লিষ্ট সকল সেবার সম্পূর্ণ দায়িত্ব আল-রাইয়ান গ্রুপ, সৌদি আরব বহন করিবে।"
            },
            {
                "num": 5,
                "title_en": "Liability and Obligation",
                "title_ar": "المسؤولية والالتزام",
                "title_bn": "দায়বদ্ধতা",
                "body_en": "According to the terms of the agreement, the candidate shall be obligated to pay 50% of 8 (eight) or 11 (eleven) months' salary, as applicable under the employment contract and regulations of the destination country and profession. If the candidate voluntarily terminates employment before completing the contractual period of 2 (two) years, a penalty of EUR 10,000 (Ten Thousand Euros) shall be payable.\n\nHowever, if during the contractual period the candidate does not receive the facilities and benefits stipulated in the contract, including accommodation, medical care, transportation, work opportunities, and salary, Al-Raiyan Group shall assume full responsibility for resolving such matters and fulfilling all related obligations.",
                "body_ar": "وفقًا لشروط العقد، يلتزم المرشح بدفع ما يعادل 50٪ من راتب 8 (ثمانية) أو 11 (أحد عشر) شهرًا، حسب ما ينص عليه عقد العمل والأنظمة المعمول بها في بلد ومجال العمل. وفي حال ترك المرشح العمل بإرادته قبل إكمال مدة العقد البالغة سنتين، فإنه يلتزم بدفع غرامة قدرها 10,000 (عشرة آلاف) يورو.\n\nوفي المقابل، إذا لم يحصل المرشح خلال مدة العقد على المزايا المنصوص عليها في العقد، مثل السكن والرعاية الطبية والمواصلات وفرصة العمل والراتب، فإن مجموعة الريان تتحمل المسؤولية الكاملة عن توفير هذه الحقوق والوفاء بجميع الالتزامات ذات الصلة.",
                "body_bn": "চুক্তির শর্তানুযায়ী, সম্মানিত প্রার্থী যে দেশ বা পেশার জন্য নিয়োগপ্রাপ্ত হবেন, সেই দেশের প্রচলিত আইন ও কর্মচুক্তি অনুযায়ী ৮ (আট) বা ১১ (এগারো) মাসের বেতনের ৫০% (পঞ্চাশ শতাংশ) পরিশোধ করতে বাধ্য থাকবেন। সম্মানিত প্রার্থী যদি চুক্তির মেয়াদ পূর্ণ হওয়ার পূর্বে, অর্থাৎ ২ (দুই) বছর সম্পন্ন হওয়ার আগে স্বেচ্ছায় চাকরি ত্যাগ করেন, তাহলে তাকে নির্ধারিত ১০,০০০ (দশ হাজার) ইউরো জরিমানা পরিশোধ করতে হবে।\n\nঅন্যদিকে, চুক্তিকালীন সময়ে যদি সম্মানিত প্রার্থী চুক্তিতে উল্লেখিত সুবিধাসমূহ—যেমন আবাসন, চিকিৎসা, যাতায়াত, কাজের সুযোগ এবং বেতন—সম্পূর্ণরূপে না পান, তবে এসব বিষয়ে উদ্ভূত সকল দায়-দায়িত্ব ও প্রয়োজনীয় ব্যবস্থা গ্রহণের সম্পূর্ণ দায়ভার আল-রাইয়ান গ্রুপ বহন করবে।"
            },
            {
                "num": 6,
                "title_en": "Visa Approval Disclaimer",
                "title_ar": "إخلاء المسؤولية بشأن التأشيرة",
                "title_bn": "ভিসা অনুমোদন সংক্রান্ত দায়মুক্তি",
                "body_en": "I shall not be held responsible for any decision relating to visa approval, rejection, suspension, or cancellation made by the competent governmental authorities.",
                "body_ar": "لا أتحمل أي مسؤولية عن قرارات الموافقة أو الرفض أو الإلغاء الصادرة عن الجهات الحكومية المختصة بالتأشيرات.",
                "body_bn": "ভিসা অনুমোদন, প্রত্যাখ্যান বা বাতিল সংক্রান্ত সিদ্ধান্ত সম্পূর্ণরূপে সংশ্লিষ্ট সরকারি কর্তৃপক্ষের এখতিয়ারভুক্ত; অতএব উক্ত বিষয়ে আমার কোনো ব্যক্তিগত দায় থাকিবে না।"
            },
            {
                "num": 7,
                "title_en": "VISA REJECTION & LIABILITY TERMS",
                "title_ar": "شروط رفض التأشيرة والمسؤولية",
                "title_bn": "ভিসা প্রত্যাখ্যান ও দায়বদ্ধতার শর্তাবলী",
                "body_en": "Visa Rejection means the refusal, cancellation, or non-issuance of a visa by the concerned government authority, embassy, immigration department, or authorized visa-issuing body after completion of the required processing steps and submission of the visa application. If the visa is rejected or delayed after completion of the processing steps due to the decision of the concerned authority or any reason beyond the Company's control, the Company shall not be responsible for such rejection or delay. Any refund or financial settlement shall be completed according to the terms and conditions specified in this agreement.",
                "body_ar": "يُقصد برفض التأشيرة عدم إصدار أو إلغاء أو رفض التأشيرة من قبل الجهة الحكومية المختصة أو السفارة أو إدارة الهجرة أو الجهة المعتمدة لإصدار التأشيرات، بعد استكمال إجراءات المعالجة المطلوبة وتقديم طلب التأشيرة. إذا تم رفض التأشيرة أو تأخيرها بعد استكمال إجراءات المعالجة بسبب قرار من الجهة المختصة أو لأي سبب خارج عن سيطرة الشركة، فلا تتحمل الشركة مسؤولية هذا الرفض أو التأخير. ويتم أي استرداد للمبلغ أو تسوية مالية وفقاً للشروط المحددة في هذه الاتفاقية.",
                "body_bn": "ভিসা প্রত্যাখ্যান বলতে বোঝাবে—প্রয়োজনীয় প্রসেসিং ধাপ সম্পন্ন ও ভিসা আবেদন জমা দেওয়ার পর সংশ্লিষ্ট সরকারি কর্তৃপক্ষ, দূতাবাস, ইমিগ্রেশন বিভাগ বা অনুমোদিত ভিসা প্রদানকারী সংস্থা কর্তৃক ভিসা প্রদান না করা, বাতিল করা বা প্রত্যাখ্যান করা। প্রসেসিং ধাপ সম্পন্ন হওয়ার পর যদি সংশ্লিষ্ট কর্তৃপক্ষের সিদ্ধান্তে এবং কোম্পানির নিয়ন্ত্রণের বাইরে কোনো কারণে ভিসা প্রত্যাখ্যান বা বিলম্ব হয়, তাহলে কোম্পানি উক্ত প্রত্যাখ্যান বা বিলম্বের জন্য দায়ী থাকবে না। অর্থ ফেরত বা আর্থিক সমাধান এই চুক্তির নির্ধারিত শর্ত অনুযায়ী সম্পন্ন হবে।"
            },
            {
                "num": 8,
                "title_en": "REFUND AUTHORIZATION",
                "title_ar": "تفويض الاسترداد",
                "title_bn": "অর্থ ফেরত প্রদানের অনুমোদন",
                "body_en": "The Company undertakes to refund 80% of the amount paid to Mr. {staff_name} in the event of a final visa rejection, for onward payment to the Candidate.",
                "body_ar": "تتعهد الشركة برد 80٪ من المبلغ المدفوع إلى السيد {staff_name} في حال الرفض النهائي للتأشيرة، ليقوم بدوره بتحويل المبلغ إلى المتقدم.",
                "body_bn": "ভিসা আবেদন চূড়ান্তভাবে প্রত্যাখ্যাত হলে কোম্পানি প্রাপ্ত অর্থের ৮০% জনাব {staff_name} এর নিকট ফেরত প্রদান করিবে, যাহা তিনি পরবর্তীতে প্রার্থীর নিকট হস্তান্তর করিবেন।"
            },
            {
                "num": 9,
                "title_en": "REFUND GUARANTEE",
                "title_ar": "ضمان الاسترداد",
                "title_bn": "অর্থ ফেরতের নিশ্চয়তা",
                "body_en": "In the event that the visa is not issued or is cancelled by the competent authorities, I undertake to obtain the refund from the Company and return 80% of the amount paid to the applicant within five (5) working days.",
                "body_ar": "في حال عدم إصدار التأشيرة أو إلغائها من قبل الجهات المختصة، أتعهد بمتابعة استرداد المبلغ من الشركة وإعادة 80٪ من المبلغ المدفوع إلى المتقدم خلال خمسة أيام عمل.",
                "body_bn": "ভিসা অনুমোদিত না হলে অথবা সংশ্লিষ্ট কর্তৃপক্ষ কর্তৃক বাতিল করা হলে, আমি কোম্পানির নিকট হইতে অর্থ আদায় সাপেক্ষে প্রদত্ত অর্থের ৮০% পাঁচ (৫) কার্যদিবসের মধ্যে প্রার্থীকে ফেরত প্রদান করিব।"
            },
            {
                "num": 10,
                "title_en": "Non-Refundable Service Charge",
                "title_ar": "رسوم الخدمة غير القابلة للاسترداد",
                "title_bn": "অফেরতযোগ্য সার্ভিস চার্জ",
                "body_en": "The remaining 20% shall be treated as administrative, processing, and service charges and shall be strictly non-refundable.",
                "body_ar": "تعتبر نسبة 20٪ من المبلغ المدفوع رسوماً إدارية ورسوم معالجة وخدمات، وهي غير قابلة للاسترداد.",
                "body_bn": "অবশিষ্ট ২০% অর্থ প্রশাসনিক, প্রসেসিং ও সার্ভিস চার্জ হিসেবে গণ্য হইবে, যাহা কোনো অবস্থাতেই ফেরতযোগ্য নহে।"
            },
            {
                "num": 11,
                "title_en": "Voluntary Withdrawal by Applicant",
                "title_ar": "انسحاب المتقدم",
                "title_bn": "আবেদনকারীর স্বেচ্ছা প্রত্যাহার",
                "body_en": "If the applicant voluntarily withdraws, cancels, or abandons the visa or employment process, no refund shall be payable.",
                "body_ar": "إذا قام المتقدم بإلغاء الطلب أو سحب إجراءات التأشيرة أو التوظيف بإرادته، فلن يكون مستحقاً لأي استرداد مالي.",
                "body_bn": "প্রার্থী নিজ উদ্যোগে আবেদন প্রত্যাহার, বাতিল বা ভিসা/চাকরি প্রক্রিয়া হইতে সরে দাঁড়াইলে প্রদত্ত অর্থের কোনো অংশ ফেরতযোগ্য হইবে না।"
            },
            {
                "num": 12,
                "title_en": "FORCE MAJEURE",
                "title_ar": "القوة القاهرة",
                "title_bn": "অনিবার্য পরিস্থিতি",
                "body_en": "If visa processing is delayed or suspended due to war, government restrictions, pandemics, regulatory changes, or circumstances beyond the Company's control, all timelines shall automatically be suspended.",
                "body_ar": "في حال تأخر أو تعليق إجراءات التأشيرة بسبب الحروب أو القيود الحكومية أو الجوائح أو التغييرات التنظيمية، تعتبر المدد الزمنية المتفق عليها معلقة تلقائياً.",
                "body_bn": "যুদ্ধ, সরকারি বিধিনিষেধ, মহামারী, আন্তর্জাতিক নিষেধাজ্ঞা বা কোম্পানির নিয়ন্ত্রণের বাইরে কোনো পরিস্থিতির কারণে ভিসা কার্যক্রম বিলম্বিত বা স্থগিত হইলে নির্ধারিত সময়সীমা স্বয়ংক্রিয়ভাবে স্থগিত বলিয়া গণ্য হইবে।"
            },
            {
                "num": 13,
                "title_en": "REFUND CLAIM REQUIREMENTS",
                "title_ar": "شروط طلب الاسترداد",
                "title_bn": "অর্থ ফেরতের শর্ত",
                "body_en": "The original receipt must be submitted for any refund claim. Photocopies, scanned copies, or lost receipts shall not be accepted.",
                "body_ar": "يشترط تقديم أصل الإيصال عند طلب أي استرداد مالي، ولن تقبل النسخ المصورة أو المفقودة.",
                "body_bn": "অর্থ ফেরতের আবেদন করিবার ক্ষেত্রে মূল রিসিট জমা প্রদান বাধ্যতামূলক। ফটোকপি, স্ক্যান কপি বা হারানো রিসিট গ্রহণযোগ্য হইবে না।"
            },
            {
                "num": 14,
                "title_en": "GOVERNING LAW & JURISDICTION",
                "title_ar": "القانون والاختصاص القضائي",
                "title_bn": "প্রযোজ্য আইন ও বিচারিক এখতিয়ার",
                "body_en": "This Agreement shall be governed by the laws of the Kingdom of Saudi Arabia. Any dispute shall be subject exclusively to the jurisdiction of the Riyadh Labor Court and the competent courts of Saudi Arabia.",
                "body_ar": "تخضع هذه الاتفاقية لأنظمة المملكة العربية السعودية، وتكون جميع النزاعات من اختصاص المحكمة العمالية بالرياض والمحاكم المختصة في المملكة العربية السعودية حصرياً.",
                "body_bn": "এই চুক্তি সৌদি আরবের প্রচলিত আইন অনুযায়ী পরিচালিত ও ব্যাখ্যাত হইবে। যেকোনো বিরোধের একমাত্র বিচারিক এখতিয়ার রিয়াদ শ্রম আদালত এবং সৌদি আরবের সংশ্লিষ্ট আদালতসমূহের উপর ন্যস্ত থাকিবে।"
            },
            {
                "num": 15,
                "title_en": "LEGAL NOTICE",
                "title_ar": "الإشعارات القانونية",
                "title_bn": "আইনি নোটিশ",
                "body_en": "Al-Raiyan Group has no office, branch, or assets in Bangladesh. Mr. {staff_name} is not authorized to receive legal notices on behalf of the Company in Bangladesh.",
                "body_ar": "لا تمتلك مجموعة الريان أي مكتب أو أصول في بنغلاديش، كما أن السيد {staff_name} ليس مفوضاً باستلام الإشعارات القانونية نيابة عن الشركة.",
                "body_bn": "আল-রাইয়ান গ্রুপের বাংলাদেশে কোনো অফিস, শাখা, প্রতিনিধি কার্যালয় বা সম্পদ নাই। জনাব {staff_name} কোম্পানির পক্ষে বাংলাদেশে কোনো আইনি নোটিশ গ্রহণের অনুমোদিত প্রতিনিধি নন।"
            },
        ]

        for clause_data in template_1_clauses:
            clause = AgreementTemplateClause.objects.create(
                template=template_1,
                clause_number=clause_data["num"],
                clause_key=slugify(clause_data["title_en"]),
                title_en=clause_data["title_en"],
                title_ar=clause_data["title_ar"],
                title_bn=clause_data["title_bn"],
                body_en=clause_data["body_en"],
                body_ar=clause_data["body_ar"],
                body_bn=clause_data["body_bn"],
                visibility_mode=ClauseVisibilityMode.INCLUDE if clause_data["num"] == 15 else ClauseVisibilityMode.ALL,
            )
            if clause_data["num"] == 15 and saudi_country:
                clause.countries.add(saudi_country)

        # -------------------------------------------------------------------
        # TEMPLATE 2
        # -------------------------------------------------------------------
        self.stdout.write("Creating Agreement Template 2 (Terms & Conditions)...")
        template_2 = AgreementTemplate.objects.create(
            title="Terms & Conditions",
            code="terms-and-conditions-v1",
            agreement_type=AgreementType.SECOND,
            version=1,
            is_active=True,
            is_default=True,
        )

        template_2_clauses = [
            {
                "num": 1,
                "body_en": "All information, documents, and papers submitted by the applicant must be accurate, truthful, and valid. If any false information, forged documents, or concealment of facts is discovered, the company reserves the right to cancel the application and deduct the necessary administrative and processing expenses.",
                "body_ar": "يجب أن تكون جميع المعلومات والمستندات والوثائق المقدمة من قبل مقدم الطلب صحيحة وصادقة وسارية المفعول. وفي حال ثبوت تقديم معلومات غير صحيحة أو مستندات مزورة أو إخفاء معلومات، يحق للشركة إلغاء الطلب وخصم المصروفات الإدارية ومصاريف المعالجة اللازمة.",
                "body_bn": "আবেদনকারী কর্তৃক প্রদত্ত সকল তথ্য, ডকুমেন্ট ও কাগজপত্র সঠিক, সত্য এবং বৈধ হতে হবে। মিথ্যা তথ্য, জাল ডকুমেন্ট বা তথ্য গোপন করার প্রমাণ পাওয়া গেলে আবেদন বাতিল হতে পারে এবং সে ক্ষেত্রে কোম্পানি প্রয়োজনীয় প্রশাসনিক ও প্রসেসিং ব্যয় কর্তনের অধিকার সংরক্ষণ করবে।"
            },
            {
                "num": 2,
                "body_en": "The company will provide documentation, profile preparation, employer submission, work permit, and visa processing services. However, the final approval of the visa, work permit, or employment is subject to the decision of the employer, embassy, and relevant government authorities.",
                "body_ar": "تقوم الشركة بتقديم خدمات إعداد المستندات والملف الشخصي، وتقديم الطلب إلى صاحب العمل، وإجراءات تصريح العمل والتأشيرة. ومع ذلك، فإن الموافقة النهائية على التأشيرة أو تصريح العمل أو الوظيفة تعتمد على قرار صاحب العمل والسفارة والجهات الحكومية المختصة.",
                "body_bn": "কোম্পানি আবেদনকারীর ডকুমেন্টেশন, প্রোফাইল প্রস্তুতি, নিয়োগকর্তার নিকট আবেদন উপস্থাপন, ওয়ার্ক পারমিট এবং ভিসা প্রসেসিং সংক্রান্ত সেবা প্রদান করবে। তবে ভিসা, ওয়ার্ক পারমিট বা চাকরির চূড়ান্ত অনুমোদন সংশ্লিষ্ট নিয়োগকর্তা, দূতাবাস এবং সরকারি কর্তৃপক্ষের সিদ্ধান্তের উপর নির্ভরশীল।"
            },
            {
                "num": 3,
                "body_en": "The company does not guarantee 100% approval of a visa, work permit, or employment. However, it will make its best professional efforts to process and manage the applicant's file appropriately.",
                "body_ar": "لا تقدم الشركة أي ضمان بنسبة 100٪ للحصول على التأشيرة أو تصريح العمل أو الوظيفة. ومع ذلك، ستبذل الشركة أقصى جهد ممكن لإدارة ملف مقدم الطلب بطريقة مهنية وسليمة.",
                "body_bn": "কোম্পানি কোনো অবস্থাতেই ১০০% ভিসা, ওয়ার্ক পারমিট অথবা চাকরি নিশ্চিত হওয়ার গ্যারান্টি প্রদান করে কুকুর। তবে আবেদনকারীর ফাইল যথাযথভাবে এবং পেশাদারিত্বের সাথে পরিচালনার সর্বোচ্চ প্রচেষ্টা অব্যাহত রাখবে।"
            },
            {
                "num": 4,
                "body_en": "The company shall not be directly responsible for any decision made by the employer, work permit authority, or embassy, as such decisions are made according to their own policies and discretion.",
                "body_ar": "لا تتحمل الشركة أي مسؤولية مباشرة عن أي قرار يصدر من صاحب العمل أو جهة تصريح العمل أو السفارة، حيث إن هذه القرارات تصدر وفقاً للسياسات والتقديرات الخاصة بالجهات المختصة.",
                "body_bn": "নিয়োগকর্তা, ওয়ার্ক পারমিট কর্তৃপক্ষ অথবা দূতাবাস কর্তৃক গৃহীত যেকোনো সিদ্ধান্তের জন্য কোম্পানি সরাসরি দায়ী থাকবে না, কারণ এসব সিদ্ধান্ত সংশ্লিষ্ট কর্তৃপক্ষের নিজস্ব নীতিমালা ও বিবেচনার ভিত্তিতে গৃহীত হয়ে থাকে।"
            },
            {
                "num": 5,
                "body_en": "If the visa is not approved, the application is canceled, or the process is not completed for any reason, the amount paid under the first receipt shall be completely non-refundable. However, 80% of the amount paid under the second receipt shall be refunded to the applicant. The remaining 20% shall be retained by the company to cover processing, documentation, administrative, communication, and other service-related expenses. Where applicable, refunds shall be paid within a maximum of five working days from the date of the relevant decision.",
                "body_ar": "في حال عدم الموافقة على التأشيرة أو إلغاء الطلب أو عدم إتمام الإجراءات لأي سبب من الأسباب، يعتبر المبلغ المدفوع بموجب الإيصال الأول غير قابل للاسترداد بالكامل. أما المبلغ المدفوع بموجب الإيصال الثاني، فيحق لمقدم الطلب استرداد 80٪ منه، بينما تحتفظ الشركة بنسبة 20٪ لتغطية تكاليف المعالجة والتوثيق والإجراءات الإدارية والاتصالات والخدمات الأخرى. وفي حال استحقاق الاسترداد، يتم دفع المبلغ خلال مدة لا تتجاوز خمسة أيام عمل من تاريخ صدور القرار.",
                "body_bn": "যেকোনো কারণে ভিসা অনুমোদিত না হলে, আবেদন বাতিল হলে অথবা প্রক্রিয়া সম্পন্ন না হলে, প্রথম রিসিটের অধীনে প্রদত্ত অর্থ সম্পূর্ণরূপে অফেরতযোগ্য (Non-Refundable) বলে গণ্য হবে। তবে দ্বিতীয় রিসিটের অধীনে প্রদত্ত মোট অর্থের ৮০% (আশি শতাংশ) আবেদনকারীকে রিফান্ড প্রদান করা হবে। অবশিষ্ট ২০% (বিশ শতাংশ) অর্থ প্রসেসিং, ডকুমেন্টেশন, প্রশাসনিক কার্যক্রম, যোগাযোগ এবং অন্যান্য সেবামূলক ব্যয়ের জন্য কোম্পানি সংরক্ষণ করবে এবং তা ব্যয় হিসেবে গণ্য হবে। রিফান্ড প্রযোজ্য হলে, সংশ্লিষ্ট সিদ্ধান্ত প্রাপ্তির তারিখ থেকে সর্বোচ্চ ৫ (পাঁচ) কর্মদিবসের মধ্যে আবেদনকারীর প্রাপ্য অর্থ ফেরত প্রদান করা হবে।"
            },
            {
                "num": 6,
                "body_en": "The refund provisions described in this Agreement shall apply only to the amount paid under the second receipt.",
                "body_ar": "تسري أحكام استرداد المبلغ المنصوص عليها في هذه الاتفاقية حصراً على المبلغ المدفوع بموجب الإيصال الثاني.",
                "body_bn": "এই চুক্তিতে বর্ণিত রিফান্ড নীতি শুধুমাত্র দ্বিতীয় রিসিটের অধীনে প্রদত্ত অর্থের ক্ষেত্রে প্রযোজ্য হবে।"
            }
        ]

        for clause_data in template_2_clauses:
            AgreementTemplateClause.objects.create(
                template=template_2,
                clause_number=clause_data["num"],
                clause_key=f"tc-clause-{clause_data['num']}",
                body_en=clause_data["body_en"],
                body_ar=clause_data["body_ar"],
                body_bn=clause_data["body_bn"],
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded templates and clauses!"))
