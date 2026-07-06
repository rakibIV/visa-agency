import os
import django
from django.core.management import call_command
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Visa_Web_Service.settings')
django.setup()

from applicant.models import AgreementTemplate, AgreementTemplateClause, ClauseVisibilityMode
from country.models import Country

def load_agreements():
    # Fetch Saudi Arabia country object for Clause 15
    saudi_arabia = Country.objects.filter(name__icontains="Saudi Arabia").first()

    # ---------------------------------------------------------
    # Template 1: Agreement Terms & Conditions
    # ---------------------------------------------------------
    t1, _ = AgreementTemplate.objects.update_or_create(
        agreement_type="MAIN",
        defaults={
            "title": "Agreement Terms & Conditions",
            "title_en": "Agreement Terms & Conditions",
            "title_ar": "شروط وأحكام الاتفاقية",
            "title_bn": "চুক্তির শর্তাবলী",
            "description": "Main agreement outlining responsibilities and refunds.",
            "is_default": True,
        }
    )

    t1_clauses = [
        {
            "clause_number": 1,
            "title_en": "ACKNOWLEDGEMENT OF RECEIPT",
            "title_ar": "إقرار الاستلام",
            "title_bn": "অর্থ গ্রহণের স্বীকৃতি",
            "body_en": "I am {representative_name}, as the authorized representative of {company_name}, {country}, hereby certify that I have received the above mentioned amount and that the said amount shall be subject to the terms and conditions stated in this receipt and agreement.",
            "body_ar": "أنا، {representative_name}، بصفتي الممثل المعتمد لـ {company_name}، {country}، أشهد بموجب هذا أنني قد استلمت المبلغ المذكور أعلاه وأن هذا المبلغ يخضع للشروط والأحكام الواردة في هذا الإيصال والاتفاقية.",
            "body_bn": "আমি {representative_name}, {company_name}, {country}-এর অনুমোদিত প্রতিনিধি হিসেবে এই মর্মে প্রত্যয়ন করিতেছি যে, উপরে উল্লিখিত অর্থ আমি গ্রহণ করিয়াছি এবং উক্ত অর্থ এই রিসিট ও চুক্তিপত্রে বর্ণিত শর্তাবলীর আওতাভুক্ত থাকিবে।"
        },
        {
            "clause_number": 2,
            "title_en": "IMPORTANT NOTICE",
            "title_ar": "إشعار هام",
            "title_bn": "গুরুত্বপূর্ণ ঘোষণা",
            "body_en": "I am {representative_name}, hereby acknowledge receipt of the above-mentioned amount on behalf of {company_name}, {country}. I shall remain responsible for the collected funds until such funds are deposited into the official company account. However, I have no authority or liability regarding visa approval or employment guarantees.",
            "body_ar": "أنا، {representative_name}، أقر باستلام المبلغ المذكور أعلاه نيابةً عن {company_name} – {country}. وأتحمل المسؤولية عن الأموال المستلمة حتى إيداعها في الحساب الرسمي للشركة. ولا أتحمل أي مسؤولية أو صلاحية فيما يتعلق بالموافقة على التأشيرة أو ضمان الوظيفة.",
            "body_bn": "আমি {representative_name}, {company_name}, {country}-এর পক্ষে উল্লিখিত অর্থ গ্রহণ করিলাম। কোম্পানির অফিসিয়াল হিসাব নম্বরে জমা প্রদান না হওয়া পর্যন্ত উক্ত অর্থের দায়িত্ব আমার উপর বর্তাইবে। তবে ভিসা অনুমোদন বা চাকরির নিশ্চয়তা প্রদানের বিষয়ে আমার কোনো ক্ষমতা বা দায়বদ্ধতা নাই।"
        },
        {
            "clause_number": 3,
            "title_en": "RESPONSIBILITY",
            "title_ar": "المسؤولية",
            "title_bn": "দায়িত্ব",
            "body_en": "Mr/Ms. {representative_name}'s responsibility is strictly limited to the collection of payments and the facilitation of the {refund_percentage}% refund in accordance with the terms of this Agreement. All responsibilities relating to visa processing, employment contracts, recruitment, and job placement shall remain the sole responsibility of {company_name}, {country}.",
            "body_ar": "تقتصر مسؤولية {representative_name} على استلام المبالغ المالية وضمان استرداد نسبة {refund_percentage}٪ وفقاً لأحكام هذه الاتفاقية. أما جميع المسؤوليات المتعلقة بالتأشيرة والتوظيف وعقود العمل فتقع حصرياً على عاتق {company_name} – {country}.",
            "body_bn": "জনাব/বেগম {representative_name}-এর দায়িত্ব কেবল অর্থ গ্রহণ এবং এই চুক্তির শর্ত অনুযায়ী {refund_percentage}% অর্থ ফেরত প্রদানের সমন্বয়ের মধ্যে সীমাবদ্ধ। ভিসা প্রসেসিং, চাকরির চুক্তিপত্র, বিদেশে নিয়োগ এবং কর্মসংস্থান সংক্রান্ত সকল দায়িত্ব একমাত্র {company_name}, {country} বহন করিবে।"
        },
        {
            "clause_number": 4,
            "title_en": "Visa & Employment Responsibility",
            "title_ar": "مسؤولية التأشيرة والتوظيف",
            "title_bn": "ভিসা ও চাকরির দায়িত্ব",
            "body_en": "{company_name} shall bear full responsibility for visa processing, recruitment, employment facilitation, and all related services in accordance with the applicable laws and regulations of {country}.",
            "body_ar": "تتحمل {company_name} المسؤولية الكاملة عن إجراءات التأشيرة والتوظيف والخدمات ذات الصلة وفقاً للأنظمة المعمول بها في {country}.",
            "body_bn": "ভিসা প্রসেসিং, নিয়োগ কার্যক্রম, চাকরি প্রদান এবং সংশ্লিষ্ট সকল সেবার সম্পূর্ণ দায়িত্ব {company_name}, {country} বহন করিবে।"
        },
        {
            "clause_number": 5,
            "title_en": "Liability and Obligation",
            "title_ar": "المسؤولية والالتزام",
            "title_bn": "দায়বদ্ধতা",
            "body_en": "According to the terms of the agreement, the candidate shall be obligated to pay 50% of 8 or 11 months' salary, as applicable under the employment contract and regulations of the destination country and profession. If the candidate voluntarily terminates employment before completing the contractual period of 2 years, a penalty of EUR 10,000 shall be payable. However, if during the contractual period the candidate does not receive the facilities and benefits stipulated in the contract, {company_name} shall assume full responsibility.",
            "body_ar": "وفقًا لشروط العقد، يلتزم المرشح بدفع ما يعادل 50٪ من راتب 8 أو 11 شهرًا، حسب ما ينص عليه عقد العمل. وفي حال ترك المرشح العمل بإرادته قبل إكمال مدة العقد البالغة سنتين، فإنه يلتزم بدفع غرامة قدرها 10,000 يورو. وفي المقابل، إذا لم يحصل المرشح على المزايا المنصوص عليها، فإن {company_name} تتحمل المسؤولية الكاملة.",
            "body_bn": "চুক্তির শর্তানুযায়ী, প্রার্থী ৮ বা ১১ মাসের বেতনের ৫০% পরিশোধ করতে বাধ্য থাকবেন। চুক্তির মেয়াদ পূর্ণ হওয়ার পূর্বে স্বেচ্ছায় চাকরি ত্যাগ করলে ১০,০০০ ইউরো জরিমানা পরিশোধ করতে হবে। অন্যদিকে, প্রার্থী চুক্তিতে উল্লেখিত সুবিধাসমূহ না পেলে {company_name} সম্পূর্ণ দায়ভার বহন করবে।"
        },
        {
            "clause_number": 6,
            "title_en": "Visa Approval Disclaimer",
            "title_ar": "إخلاء المسؤولية بشأن التأشيرة",
            "title_bn": "ভিসা অনুমোদন সংক্রান্ত দায়মুক্তি",
            "body_en": "I shall not be held responsible for any decision relating to visa approval, rejection, suspension, or cancellation made by the competent governmental authorities.",
            "body_ar": "لا أتحمل أي مسؤولية عن قرارات الموافقة أو الرفض أو الإلغاء الصادرة عن الجهات الحكومية المختصة بالتأشيرات.",
            "body_bn": "ভিসা অনুমোদন, প্রত্যাখ্যান বা বাতিল সংক্রান্ত সিদ্ধান্ত সম্পূর্ণরূপে সংশ্লিষ্ট সরকারি কর্তৃপক্ষের এখতিয়ারভুক্ত; অতএব উক্ত বিষয়ে আমার কোনো ব্যক্তিগত দায় থাকিবে না।"
        },
        {
            "clause_number": 7,
            "title_en": "VISA REJECTION & LIABILITY TERMS",
            "title_ar": "شروط رفض التأشيرة والمسؤولية",
            "title_bn": "ভিসা প্রত্যাখ্যান ও দায়বদ্ধতার শর্তাবলী",
            "body_en": "Visa Rejection means the refusal, cancellation, or non-issuance of a visa by the concerned authority. If the visa is rejected or delayed after completion of the processing steps due to the decision of the concerned authority or any reason beyond the Company's control, the Company shall not be responsible. Any refund shall be completed according to the terms specified.",
            "body_ar": "إذا تم رفض التأشيرة أو تأخيرها بعد استكمال إجراءات المعالجة بسبب قرار من الجهة المختصة أو لأي سبب خارج عن سيطرة الشركة، فلا تتحمل الشركة مسؤولية هذا الرفض أو التأخير.",
            "body_bn": "প্রসেসিং ধাপ সম্পন্ন হওয়ার পর কর্তৃপক্ষের সিদ্ধান্তে এবং কোম্পানির নিয়ন্ত্রণের বাইরে কোনো কারণে ভিসা প্রত্যাখ্যান বা বিলম্ব হলে, কোম্পানি দায়ী থাকবে না। অর্থ ফেরত এই চুক্তির শর্ত অনুযায়ী সম্পন্ন হবে।"
        },
        {
            "clause_number": 8,
            "title_en": "REFUND AUTHORIZATION",
            "title_ar": "تفويض الاسترداد",
            "title_bn": "অর্থ ফেরত প্রদানের অনুমোদন",
            "body_en": "The Company undertakes to refund {refund_percentage}% of the amount paid to {representative_name} in the event of a final visa rejection, for onward payment to the Candidate.",
            "body_ar": "تتعهد الشركة برد {refund_percentage}٪ من المبلغ المدفوع إلى {representative_name} في حال الرفض النهائي للتأشيرة، ليقوم بدوره بتحويل المبلغ إلى المتقدم.",
            "body_bn": "ভিসা আবেদন চূড়ান্তভাবে প্রত্যাখ্যাত হলে কোম্পানি প্রাপ্ত অর্থের {refund_percentage}% {representative_name}-এর নিকট ফেরত প্রদান করিবে, যাহা তিনি পরবর্তীতে প্রার্থীর নিকট হস্তান্তর করিবেন।"
        },
        {
            "clause_number": 9,
            "title_en": "REFUND GUARANTEE",
            "title_ar": "ضمان الاسترداد",
            "title_bn": "অর্থ ফেরতের নিশ্চয়তা",
            "body_en": "In the event that the visa is not issued or is cancelled by the competent authorities, I undertake to obtain the refund from the Company and return {refund_percentage}% of the amount paid to the applicant within five (5) working days.",
            "body_ar": "في حال عدم إصدار التأشيرة أو إلغائها من قبل الجهات المختصة، أتعهد بمتابعة استرداد المبلغ من الشركة وإعادة {refund_percentage}٪ من المبلغ المدفوع إلى المتقدم خلال خمسة أيام عمل.",
            "body_bn": "ভিসা অনুমোদিত না হলে অথবা সংশ্লিষ্ট কর্তৃপক্ষ কর্তৃক বাতিল করা হলে, আমি কোম্পানির নিকট হইতে অর্থ আদায় সাপেক্ষে প্রদত্ত অর্থের {refund_percentage}% পাঁচ (৫) কার্যদিবসের মধ্যে প্রার্থীকে ফেরত প্রদান করিব।"
        },
        {
            "clause_number": 10,
            "title_en": "Non-Refundable Service Charge",
            "title_ar": "رسوم الخدمة غير القابلة للاسترداد",
            "title_bn": "অফেরতযোগ্য সার্ভিস চার্জ",
            "body_en": "The remaining amount shall be treated as administrative, processing, and service charges and shall be strictly non-refundable.",
            "body_ar": "تعتبر النسبة المتبقية من المبلغ المدفوع رسوماً إدارية ورسوم معالجة وخدمات، وهي غير قابلة للاسترداد.",
            "body_bn": "অবশিষ্ট অর্থ প্রশাসনিক, প্রসেসিং ও সার্ভিস চার্জ হিসেবে গণ্য হইবে, যাহা কোনো অবস্থাতেই ফেরতযোগ্য নহে।"
        },
        {
            "clause_number": 11,
            "title_en": "Voluntary Withdrawal by Applicant",
            "title_ar": "انسحاب المتقدم",
            "title_bn": "আবেদনকারীর স্বেচ্ছা প্রত্যাহার",
            "body_en": "If the applicant voluntarily withdraws, cancels, or abandons the visa or employment process, no refund shall be payable.",
            "body_ar": "إذا قام المتقدم بإلغاء الطلب أو سحب إجراءات التأشيرة أو التوظيف بإرادته، فلن يكون مستحقاً لأي استرداد مالي.",
            "body_bn": "প্রার্থী নিজ উদ্যোগে আবেদন প্রত্যাহার, বাতিল বা ভিসা/চাকরি প্রক্রিয়া হইতে সরে দাঁড়াইলে প্রদত্ত অর্থের কোনো অংশ ফেরতযোগ্য হইবে না।"
        },
        {
            "clause_number": 12,
            "title_en": "FORCE MAJEURE",
            "title_ar": "القوة القاهرة",
            "title_bn": "অনিবার্য পরিস্থিতি",
            "body_en": "If visa processing is delayed or suspended due to war, government restrictions, pandemics, regulatory changes, or circumstances beyond the Company's control, all timelines shall automatically be suspended.",
            "body_ar": "في حال تأخر أو تعليق إجراءات التأشيرة بسبب الحروب أو القيود الحكومية أو الجوائح أو التغييرات التنظيمية، تعتبر المدد الزمنية المتفق عليها معلقة تلقائياً.",
            "body_bn": "যুদ্ধ, সরকারি বিধিনিষেধ, মহামারী, আন্তর্জাতিক নিষেধাজ্ঞা বা কোম্পানির নিয়ন্ত্রণের বাইরে কোনো পরিস্থিতির কারণে ভিসা কার্যক্রম বিলম্বিত বা স্থগিত হইলে নির্ধারিত সময়সীমা স্বয়ংক্রিয়ভাবে স্থগিত বলিয়া গণ্য হইবে।"
        },
        {
            "clause_number": 13,
            "title_en": "REFUND CLAIM REQUIREMENTS",
            "title_ar": "شروط طلب الاسترداد",
            "title_bn": "অর্থ ফেরতের শর্ত",
            "body_en": "The original receipt must be submitted for any refund claim. Photocopies, scanned copies, or lost receipts shall not be accepted.",
            "body_ar": "يشترط تقديم أصل الإيصال عند طلب أي استرداد مالي، ولن تقبل النسخ المصورة أو المفقودة.",
            "body_bn": "অর্থ ফেরতের আবেদন করিবার ক্ষেত্রে মূল রিসিট জমা প্রদান বাধ্যতামূলক। ফটোকপি, স্ক্যান কপি বা হারানো রিসিট গ্রহণযোগ্য হইবে না।"
        },
        {
            "clause_number": 14,
            "title_en": "GOVERNING LAW & JURISDICTION",
            "title_ar": "القانون والاختصاص القضائي",
            "title_bn": "প্রযোজ্য আইন ও বিচারিক এখতিয়ার",
            "body_en": "This Agreement shall be governed by the laws of {country}. Any dispute shall be subject exclusively to the jurisdiction of the competent courts of {country}.",
            "body_ar": "تخضع هذه الاتفاقية لأنظمة {country}، وتكون جميع النزاعات من اختصاص المحاكم المختصة في {country} حصرياً.",
            "body_bn": "এই চুক্তি {country}-এর প্রচলিত আইন অনুযায়ী পরিচালিত ও ব্যাখ্যাত হইবে। যেকোনো বিরোধের একমাত্র বিচারিক এখতিয়ার {country}-এর সংশ্লিষ্ট আদালতসমূহের উপর ন্যস্ত থাকিবে।"
        },
        {
            "clause_number": 15,
            "title_en": "LEGAL NOTICE",
            "title_ar": "الإشعارات القانونية",
            "title_bn": "আইনি নোটিশ",
            "body_en": "{company_name} has no office, branch, or assets in Bangladesh. {representative_name} is not authorized to receive legal notices on behalf of the Company in Bangladesh.",
            "body_ar": "لا تمتلك {company_name} أي مكتب أو أصول في بنغلاديش، كما أن {representative_name} ليس مفوضاً باستلام الإشعارات القانونية نيابة عن الشركة.",
            "body_bn": "{company_name}-এর বাংলাদেশে কোনো অফিস, শাখা, প্রতিনিধি কার্যালয় বা সম্পদ নাই। {representative_name} কোম্পানির পক্ষে বাংলাদেশে কোনো আইনি নোটিশ গ্রহণের অনুমোদিত প্রতিনিধি নন.",
            "visibility_mode": ClauseVisibilityMode.INCLUDE if saudi_arabia else ClauseVisibilityMode.ALL,
        }
    ]

    for clause in t1_clauses:
        obj, _ = AgreementTemplateClause.objects.update_or_create(
            template=t1,
            clause_number=clause["clause_number"],
            defaults={
                "title_en": clause["title_en"],
                "title_ar": clause["title_ar"],
                "title_bn": clause["title_bn"],
                "body_en": clause["body_en"],
                "body_ar": clause["body_ar"],
                "body_bn": clause["body_bn"],
                "clause_key": slugify(clause["title_en"][:50]),
                "visibility_mode": clause.get("visibility_mode", ClauseVisibilityMode.ALL)
            }
        )
        if obj.visibility_mode == ClauseVisibilityMode.INCLUDE and saudi_arabia:
            obj.countries.add(saudi_arabia)


    # ---------------------------------------------------------
    # Template 2: Terms & Conditions
    # ---------------------------------------------------------
    t2, _ = AgreementTemplate.objects.update_or_create(
        agreement_type="SECOND",
        defaults={
            "title": "Terms & Conditions",
            "title_en": "Terms & Conditions",
            "title_ar": "الشروط والأحكام",
            "title_bn": "শর্তাবলী",
            "description": "Applicant terms and conditions regarding accurate information and processing.",
            "is_default": True,
        }
    )

    t2_clauses = [
        {
            "clause_number": 1,
            "title_en": "Accuracy of Information",
            "title_ar": "دقة المعلومات",
            "title_bn": "তথ্য সঠিকতা",
            "body_en": "All information, documents, and papers submitted by the applicant must be accurate, truthful, and valid. If any false information, forged documents, or concealment of facts is discovered, the company reserves the right to cancel the application and deduct the necessary administrative and processing expenses.",
            "body_ar": "يجب أن تكون جميع المعلومات والمستندات والوثائق المقدمة من قبل مقدم الطلب صحيحة وصادقة وسارية المفعول.",
            "body_bn": "আবেদনকারী কর্তৃক প্রদত্ত সকল তথ্য, ডকুমেন্ট ও কাগজপত্র সঠিক, সত্য এবং বৈধ হতে হবে। মিথ্যা তথ্য, জাল ডকুমেন্ট বা তথ্য গোপন করার প্রমাণ পাওয়া গেলে আবেদন বাতিল হতে পারে।"
        },
        {
            "clause_number": 2,
            "title_en": "Services Provided",
            "title_ar": "الخدمات",
            "title_bn": "সেবাসমূহ",
            "body_en": "The company will provide documentation, profile preparation, employer submission, work permit, and visa processing services. However, the final approval of the visa, work permit, or employment is subject to the decision of the employer, embassy, and relevant government authorities.",
            "body_ar": "تقوم الشركة بتقديم خدمات إعداد المستندات والملف الشخصي، وتقديم الطلب إلى صاحب العمل، وإجراءات تصريح العمل والتأشيرة.",
            "body_bn": "কোম্পানি আবেদনকারীর ডকুমেন্টেশন, প্রোফাইল প্রস্তুতি, নিয়োগকর্তার নিকট আবেদন উপস্থাপন, ওয়ার্ক পারমিট এবং ভিসা প্রসেসিং সংক্রান্ত সেবা প্রদান করবে।"
        },
        {
            "clause_number": 3,
            "title_en": "No Guarantee",
            "title_ar": "لا يوجد ضمان",
            "title_bn": "কোন গ্যারান্টি নেই",
            "body_en": "The company does not guarantee 100% approval of a visa, work permit, or employment. However, it will make its best professional efforts to process and manage the applicant’s file appropriately.",
            "body_ar": "لا تقدم الشركة أي ضمان بنسبة 100٪ للحصول على التأشيرة أو تصريح العمل أو الوظيفة.",
            "body_bn": "কোম্পানি কোনো অবস্থাতেই ১০০% ভিসা, ওয়ার্ক পারমিট অথবা চাকরি নিশ্চিত হওয়ার গ্যারান্টি প্রদান করে না।"
        },
        {
            "clause_number": 4,
            "title_en": "Decisions by Authorities",
            "title_ar": "القرارات",
            "title_bn": "সিদ্ধান্তসমূহ",
            "body_en": "The company shall not be directly responsible for any decision made by the employer, work permit authority, or embassy, as such decisions are made according to their own policies and discretion.",
            "body_ar": "لا تتحمل الشركة أي مسؤولية مباشرة عن أي قرار يصدر من صاحب العمل أو جهة تصريح العمل أو السفارة.",
            "body_bn": "নিয়োগকর্তা, ওয়ার্ক পারমিট কর্তৃপক্ষ অথবা দূতাবাস কর্তৃক গৃহীত যেকোনো সিদ্ধান্তের জন্য কোম্পানি সরাসরি দায়ী থাকবে না।"
        },
        {
            "clause_number": 5,
            "title_en": "Refund Rules for Payments",
            "title_ar": "قواعد الاسترداد",
            "title_bn": "অর্থ ফেরত নিয়মাবলী",
            "body_en": "If the visa is not approved, the application is canceled, or the process is not completed for any reason, the amount paid under the first receipt shall be completely non-refundable. However, {refund_percentage}% of the amount paid under the second receipt shall be refunded to the applicant. The remaining 20% shall be retained by the company to cover processing, documentation, administrative, communication, and other service-related expenses. Where applicable, refunds shall be paid within a maximum of five working days from the date of the relevant decision.",
            "body_ar": "في حال عدم الموافقة على التأشيرة أو إلغاء الطلب أو عدم إتمام الإجراءات لأي سبب من الأسباب، يعتبر المبلغ المدفوع بموجب الإيصال الأول غير قابل للاسترداد بالكامل. أما المبلغ المدفوع بموجب الإيصال الثاني، فيحق لمقدم الطلب استرداد {refund_percentage}٪ منه، بينما تحتفظ الشركة بنسبة 20٪ لتغطية تكاليف المعالجة والتوثيق والإجراءات الإدارية والاتصالات والخدمات الأخرى. وفي حال استحقاق الاسترداد، يتم دفع المبلغ خلال مدة لا تتجاوز خمسة أيام عمل من تاريخ صدور القرار.",
            "body_bn": "যেকোনো কারণে ভিসা অনুমোদিত না হলে, আবেদন বাতিল হলে অথবা প্রক্রিয়া সম্পন্ন না হলে, প্রথম রিসিটের অধীনে প্রদত্ত অর্থ সম্পূর্ণরূপে অফেরতযোগ্য (Non-Refundable) বলে গণ্য হবে। তবে দ্বিতীয় রিসিটের অধীনে প্রদত্ত মোট অর্থের {refund_percentage}% (আশি শতাংশ) আবেদনকারীকে রিফান্ড প্রদান করা হবে। অবশিষ্ট ২০% (বিশ শতাংশ) অর্থ প্রসেসিং, ডকুমেন্টেশন, প্রশাসনিক কার্যক্রম, যোগাযোগ এবং অন্যান্য সেবামূলক ব্যয়ের জন্য কোম্পানি সংরক্ষণ করবে এবং তা ব্যয় হিসেবে গণ্য হবে। রিফান্ড প্রযোজ্য হলে, সংশ্লিষ্ট সিদ্ধান্ত প্রাপ্তির তারিখ থেকে সর্বোচ্চ ৫ (পাঁচ) কর্মদিবসের মধ্যে আবেদনকারীর প্রাপ্য অর্থ ফেরত প্রদান করা হবে।"
        },
        {
            "clause_number": 6,
            "title_en": "Applicability of Refunds",
            "title_ar": "سريان أحكام الاسترداد",
            "title_bn": "রিফান্ডের প্রযোজ্যতা",
            "body_en": "The refund provisions described in this Agreement shall apply only to the amount paid under the second receipt.",
            "body_ar": "تسري أحكام استرداد المبلغ المنصوص عليها في هذه الاتفاقية حصراً على المبلغ المدفوع بموجب الإيصال الثاني.",
            "body_bn": "এই চুক্তিতে বর্ণিত রিফান্ড নীতি শুধুমাত্র দ্বিতীয় রিসিটের অধীনে প্রদত্ত অর্থের ক্ষেত্রে প্রযোজ্য হবে।"
        },
        {
            "clause_number": 7,
            "title_en": "REFUND OF SECOND PAYMENT",
            "title_ar": "استرداد الدفعة الثانية",
            "title_bn": "দ্বিতীয় কিস্তির অর্থ ফেরতের তথ্য",
            "body_en": "If a refund of the second payment is applicable in accordance with the terms and conditions of the agreement, {refund_percentage}% of the second payment amount shall be refunded to the bank account provided by the applicant.",
            "body_ar": "إذا كان استرداد الدفعة الثانية مستحقاً وفقاً لشروط وأحكام العقد، فسيتم تحويل {refund_percentage}٪ من قيمة الدفعة الثانية إلى الحساب البنكي الذي حدده مقدم الطلب.",
            "body_bn": "চুক্তির শর্তাবলী অনুযায়ী যদি দ্বিতীয় রিসিভ/দ্বিতীয় কিস্তির অর্থ রিফান্ড প্রযোজ্য হয়, তাহলে দ্বিতীয় রিসিভে জমা দেওয়া টাকার {refund_percentage}% আবেদনকারীর প্রদানকৃত ব্যাংক অ্যাকাউন্টে ফেরত পাঠানো হবে।"
        }
    ]

    for clause in t2_clauses:
        AgreementTemplateClause.objects.update_or_create(
            template=t2,
            clause_number=clause["clause_number"],
            defaults={
                "title_en": clause["title_en"],
                "title_ar": clause["title_ar"],
                "title_bn": clause["title_bn"],
                "body_en": clause["body_en"],
                "body_ar": clause["body_ar"],
                "body_bn": clause["body_bn"],
                "clause_key": slugify(clause["title_en"][:50])
            }
        )

    # ---------------------------------------------------------
    # Template 3: Declaration
    # ---------------------------------------------------------
    t3, _ = AgreementTemplate.objects.update_or_create(
        agreement_type="THIRD",
        defaults={
            "title": "Declaration",
            "title_en": "Declaration",
            "title_ar": "إقرار",
            "title_bn": "ঘোষণা",
            "description": "Applicant's final declaration regarding terms and refund policies.",
            "is_default": True,
        }
    )

    t3_clauses = [
        {
            "clause_number": 1,
            "title_en": "DECLARATION",
            "title_ar": "إقرار",
            "title_bn": "ঘোষণা",
            "body_en": "I have read, understood, and agree to the terms and conditions of the Agreement, including the refund policy.",
            "body_ar": "لقد قرأت وفهمت ووافقت على شروط وأحكام الاتفاقية، بما في ذلك سياسة استرداد المبلغ.",
            "body_bn": "আমি চুক্তির সকল শর্তাবলী ও নিয়ম ভালোভাবে পড়েছি, বুঝেছি এবং রিফান্ড নীতিসহ চুক্তির শর্তাবলীতে সম্মত আছি।"
        }
    ]

    for clause in t3_clauses:
        AgreementTemplateClause.objects.update_or_create(
            template=t3,
            clause_number=clause["clause_number"],
            defaults={
                "title_en": clause["title_en"],
                "title_ar": clause["title_ar"],
                "title_bn": clause["title_bn"],
                "body_en": clause["body_en"],
                "body_ar": clause["body_ar"],
                "body_bn": clause["body_bn"],
                "clause_key": slugify(clause["title_en"][:50])
            }
        )

    print("All Three Agreement Templates and Clauses generated successfully.")

    # Dump the new data
    with open('dummy_data.json', 'w', encoding='utf-8') as f:
        call_command(
            'dumpdata', 
            'staff.Designation',
            'staff.Staff',
            'country.Country', 
            'country.CountryRequirement',
            'country.CountryFAQ',
            'visa.VisaCategory', 
            'visa.Visa', 
            'visa.VisaRequirement',
            'visa.VisaJob',
            'visa.VisaStep',
            'visa.VisaFAQ',
            'visa.JobFacility',
            'applicant.ApplicationStatus', 
            'applicant.Applicant',
            'applicant.ApplicantProfile',
            'applicant.ApplicantAddress',
            'applicant.ApplicantPayment',
            'applicant.ApplicantDocument',
            'applicant.AgreementTemplate',
            'applicant.AgreementTemplateClause',
            indent=4, 
            stdout=f
        )
    print("dumpdata updated in dummy_data.json.")

if __name__ == '__main__':
    load_agreements()
